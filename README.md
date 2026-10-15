# Enterprise Automatic Loan Approval System (ALAS)

An enterprise-grade, cloud-native automated consumer lending platform featuring high-throughput loan ingestion, sub-second automated credit underwriting decisioning, Role-Based Access Control (RBAC), and interactive loan officer workbenches.

---

## 🚀 Key Features

- **Automated Underwriting Engine**: Sub-second decisioning evaluating credit scores and Debt-to-Income (DTI) metrics against regulatory credit policy rules.
- **Enterprise UI Workbenches**:
  - `Dashboard`: Real-time processing volume, straight-through approval rates, and decision latencies.
  - `Applications Queue`: Full-text search and status filtering across all intake applications.
  - `Application Details`: Deep applicant financial profiles, terms, and decision audit logs.
  - `Manual Review Workbench`: Interactive underwriter adjudication (`Approve`, `Deny`, `Request Info`).
  - `Reporting & Analytics`: Regulatory compliance reporting, throughput summaries, and audit logs.
  - `User & Role Management`: Administration of enterprise users and RBAC assignments.
- **Security & RBAC**: OAuth2/OIDC token simulation enforcing role-based permissions (`Administrator`, `Reviewer`, `Auditor`, `Developer`).
- **12-Factor Configuration**: Environment isolation with PostgreSQL & Redis Docker Compose definitions.

---

## 🛠️ Quick Start

### 1. Local Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Platform
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Navigate to `http://localhost:8000` to access the enterprise web portal.

### 3. Run Test Suite
```bash
pytest
```
