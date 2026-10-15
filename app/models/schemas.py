from typing import List, Optional
from pydantic import BaseModel, EmailStr

# --- Health Check ---
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str

# --- Auth & User Models ---
class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    role: str
    status: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserProfile(BaseModel):
    user_id: str
    full_name: str
    email: str
    role: str
    permissions: List[str]

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "Reviewer"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

# --- Loan Application Models ---
class LoanApplicationCreate(BaseModel):
    applicant_name: str
    dob: str
    email: str
    phone: str
    address: str
    loan_type: str = "Personal"
    amount_requested: float
    loan_term_months: int = 36
    credit_score: int
    annual_income: float
    debt_to_income_ratio: float
    employer_name: Optional[str] = ""

class LoanApplicationSubmissionResponse(BaseModel):
    id: str
    status: str
    decision_notes: str
    decision_time_ms: float
    submitted_at: str

class LoanApplicationListItem(BaseModel):
    id: str
    applicant_name: str
    loan_type: str
    amount: float
    submitted_at: str
    status: str

class LoanApplicationsListResponse(BaseModel):
    total: int
    applications: List[LoanApplicationListItem]

class ApplicantInfo(BaseModel):
    name: str
    dob: str
    email: str
    phone: str
    address: str

class LoanDetails(BaseModel):
    loan_type: str
    amount_requested: float
    loan_term_months: int
    credit_score: int
    annual_income: float
    debt_to_income_ratio: float
    employer_name: Optional[str] = None

class DecisionHistoryItem(BaseModel):
    timestamp: str
    stage: str
    outcome: str
    notes: str
    performer: str

class LoanApplicationDetail(BaseModel):
    id: str
    status: str
    decision_reason: Optional[str] = None
    applicant: ApplicantInfo
    loan_details: LoanDetails
    decision_history: List[DecisionHistoryItem]

# --- Adjudication Workbench ---
class AdjudicationRequest(BaseModel):
    action: str  # APPROVE, DENY, REQUEST_INFO
    review_notes: str

class AdjudicationResponse(BaseModel):
    id: str
    status: str
    adjudicated_by: str
    adjudicated_at: str
    message: str

# --- Dashboard & Reports ---
class DashboardMetricsResponse(BaseModel):
    applications_today: int
    applications_change_pct: float
    approval_rate_pct: float
    approval_rate_change_pct: float
    manual_review_count: int
    manual_review_change: int
    avg_decision_time_sec: float

class VolumeHistoryItem(BaseModel):
    date: str
    submitted: int
    approved: int
    rejected: int
    manual_review: int

class VolumeHistoryResponse(BaseModel):
    history: List[VolumeHistoryItem]

class ReportSummaryItem(BaseModel):
    date: str
    submitted: int
    auto_approved: int
    auto_rejected: int
    manual_review: int
    final_approved: int
    final_rejected: int

class ReportResponse(BaseModel):
    report_type: str
    start_date: str
    end_date: str
    summary: List[ReportSummaryItem]
