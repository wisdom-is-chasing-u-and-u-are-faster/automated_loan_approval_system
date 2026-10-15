from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.models.schemas import (
    LoanApplicationCreate,
    LoanApplicationSubmissionResponse,
    LoanApplicationsListResponse,
    LoanApplicationListItem,
    LoanApplicationDetail,
    ApplicantInfo,
    LoanDetails,
    DecisionHistoryItem,
    AdjudicationRequest,
    AdjudicationResponse
)
from app.core.security import get_current_user_payload, require_role
from app.services.loan_decision_engine import LoanDecisionEngine
from app.db.session import get_db

router = APIRouter(prefix="/applications", tags=["Loan Applications & Underwriting Engine"])

@router.get("", response_model=LoanApplicationsListResponse)
def list_applications(
    status: Optional[str] = Query(None, description="Filter by status (PENDING, APPROVED, REJECTED, MANUAL_REVIEW)"),
    search: Optional[str] = Query(None, description="Search applicant name or ID"),
    current_user: dict = Depends(get_current_user_payload)
):
    """Retrieves loan applications queue with status and keyword filtering."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT app_id, applicant_name, loan_type, amount_requested, submitted_at, status FROM loan_applications WHERE 1=1"
        params = []
        
        if status and status.upper() != "ALL":
            query += " AND UPPER(status) = ?"
            params.append(status.upper().replace(" ", "_"))
            
        if search:
            query += " AND (applicant_name LIKE ? OR app_id LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
            
        query += " ORDER BY id DESC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        apps = [
            LoanApplicationListItem(
                id=r["app_id"],
                applicant_name=r["applicant_name"],
                loan_type=r["loan_type"],
                amount=float(r["amount_requested"]),
                submitted_at=str(r["submitted_at"]),
                status=r["status"]
            )
            for r in rows
        ]
        
        return LoanApplicationsListResponse(total=len(apps), applications=apps)

@router.post("", response_model=LoanApplicationSubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_loan_application(
    app_data: LoanApplicationCreate,
    current_user: dict = Depends(get_current_user_payload)
):
    """
    Ingests consumer loan application and executes sub-second automated underwriting decision engine.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Generate unique application ID
        app_id = LoanDecisionEngine.generate_next_app_id(conn)
        
        # 2. Execute automated decision rules
        decision_status, decision_reason, decision_time_ms = LoanDecisionEngine.evaluate_application(
            credit_score=app_data.credit_score,
            debt_to_income_ratio=app_data.debt_to_income_ratio,
            annual_income=app_data.annual_income,
            amount_requested=app_data.amount_requested
        )
        
        submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        decided_at = submitted_at if decision_status in ["APPROVED", "REJECTED"] else None
        
        # 3. Persist loan application
        cursor.execute(
            """
            INSERT INTO loan_applications (
                app_id, applicant_name, dob, email, phone, address,
                loan_type, amount_requested, loan_term_months, credit_score,
                annual_income, debt_to_income_ratio, employer_name,
                status, decision_reason, decision_time_ms, submitted_at, decided_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                app_id, app_data.applicant_name, app_data.dob, app_data.email, app_data.phone, app_data.address,
                app_data.loan_type, app_data.amount_requested, app_data.loan_term_months, app_data.credit_score,
                app_data.annual_income, app_data.debt_to_income_ratio, app_data.employer_name,
                decision_status, decision_reason, decision_time_ms, submitted_at, decided_at
            )
        )
        
        # 4. Record decision history stages
        cursor.execute(
            "INSERT INTO decision_history (app_id, stage, outcome, notes, performer, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (app_id, "Initial Submission", "Received", "Application received via Ingestion API Gateway.", current_user.get("full_name", "Ingestion Gateway"), submitted_at)
        )
        
        outcome_label = "Auto-Approved" if decision_status == "APPROVED" else ("Auto-Rejected" if decision_status == "REJECTED" else "Flagged for Review")
        cursor.execute(
            "INSERT INTO decision_history (app_id, stage, outcome, notes, performer, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (app_id, "Automated Check", outcome_label, decision_reason, "Automated Rules Engine", submitted_at)
        )
        
        return LoanApplicationSubmissionResponse(
            id=app_id,
            status=decision_status,
            decision_notes=decision_reason,
            decision_time_ms=decision_time_ms,
            submitted_at=submitted_at
        )

@router.get("/queue/manual-review", response_model=LoanApplicationsListResponse)
def get_manual_review_queue(current_user: dict = Depends(require_role(["Reviewer", "Administrator"]))):
    """Retrieves list of applications currently in MANUAL_REVIEW state."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT app_id, applicant_name, loan_type, amount_requested, submitted_at, status FROM loan_applications WHERE status = 'MANUAL_REVIEW' ORDER BY id ASC"
        )
        rows = cursor.fetchall()
        apps = [
            LoanApplicationListItem(
                id=r["app_id"],
                applicant_name=r["applicant_name"],
                loan_type=r["loan_type"],
                amount=float(r["amount_requested"]),
                submitted_at=str(r["submitted_at"]),
                status=r["status"]
            )
            for r in rows
        ]
        return LoanApplicationsListResponse(total=len(apps), applications=apps)

@router.get("/{app_id}", response_model=LoanApplicationDetail)
def get_application_details(app_id: str, current_user: dict = Depends(get_current_user_payload)):
    """Retrieves full application details, applicant profile, loan terms, and decision audit timeline."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM loan_applications WHERE app_id = ?", (app_id,))
        app_row = cursor.fetchone()
        
        if not app_row:
            raise HTTPException(status_code=404, detail=f"Loan Application '{app_id}' not found")
        
        # Fetch decision history
        cursor.execute("SELECT stage, outcome, notes, performer, timestamp FROM decision_history WHERE app_id = ? ORDER BY id ASC", (app_id,))
        history_rows = cursor.fetchall()
        
        history = [
            DecisionHistoryItem(
                timestamp=str(h["timestamp"]),
                stage=h["stage"],
                outcome=h["outcome"],
                notes=h["notes"] or "",
                performer=h["performer"] or "System"
            )
            for h in history_rows
        ]
        
        return LoanApplicationDetail(
            id=app_row["app_id"],
            status=app_row["status"],
            decision_reason=app_row["decision_reason"],
            applicant=ApplicantInfo(
                name=app_row["applicant_name"],
                dob=app_row["dob"],
                email=app_row["email"],
                phone=app_row["phone"],
                address=app_row["address"]
            ),
            loan_details=LoanDetails(
                loan_type=app_row["loan_type"],
                amount_requested=float(app_row["amount_requested"]),
                loan_term_months=int(app_row["loan_term_months"]),
                credit_score=int(app_row["credit_score"]),
                annual_income=float(app_row["annual_income"]),
                debt_to_income_ratio=float(app_row["debt_to_income_ratio"]),
                employer_name=app_row["employer_name"]
            ),
            decision_history=history
        )

@router.post("/{app_id}/adjudicate", response_model=AdjudicationResponse)
def adjudicate_application(
    app_id: str,
    adj_data: AdjudicationRequest,
    current_user: dict = Depends(require_role(["Reviewer", "Administrator"]))
):
    """
    Performs underwriter manual review adjudication action (APPROVE / DENY / REQUEST_INFO).
    """
    action_upper = adj_data.action.upper().strip()
    status_map = {
        "APPROVE": "APPROVED",
        "APPROVED": "APPROVED",
        "DENY": "REJECTED",
        "REJECT": "REJECTED",
        "DENIED": "REJECTED",
        "REQUEST_INFO": "INFO_REQUESTED",
        "REQUEST MORE INFORMATION": "INFO_REQUESTED",
        "INFO_REQUESTED": "INFO_REQUESTED"
    }
    
    if action_upper not in status_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid adjudication action '{adj_data.action}'. Allowed: APPROVE, DENY, REQUEST_INFO"
        )
    
    new_status = status_map[action_upper]
    adjudicated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    performer_name = current_user.get("full_name", "Enterprise Underwriter")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM loan_applications WHERE app_id = ?", (app_id,))
        app_row = cursor.fetchone()
        
        if not app_row:
            raise HTTPException(status_code=404, detail=f"Loan Application '{app_id}' not found")
        
        # Update loan application status
        cursor.execute(
            "UPDATE loan_applications SET status = ?, decision_reason = ?, decided_at = ? WHERE app_id = ?",
            (new_status, adj_data.review_notes, adjudicated_at, app_id)
        )
        
        # Add to decision history audit trail
        stage_name = "Manual Adjudication"
        outcome_name = f"Manually {new_status.title()}"
        cursor.execute(
            "INSERT INTO decision_history (app_id, stage, outcome, notes, performer, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (app_id, stage_name, outcome_name, adj_data.review_notes, performer_name, adjudicated_at)
        )
        
        return AdjudicationResponse(
            id=app_id,
            status=new_status,
            adjudicated_by=performer_name,
            adjudicated_at=adjudicated_at,
            message=f"Application {app_id} successfully transitioned to {new_status}."
        )
