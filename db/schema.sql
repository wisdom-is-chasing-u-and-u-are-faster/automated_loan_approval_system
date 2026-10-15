-- ==============================================================================
-- Enterprise Automatic Loan Approval System (ALAS) Relational DDL Schema
-- ==============================================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Reviewer',
    status VARCHAR(50) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id VARCHAR(50) UNIQUE NOT NULL,
    applicant_name VARCHAR(255) NOT NULL,
    dob VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    loan_type VARCHAR(100) NOT NULL,
    amount_requested DECIMAL(12, 2) NOT NULL,
    loan_term_months INTEGER NOT NULL,
    credit_score INTEGER NOT NULL,
    annual_income DECIMAL(12, 2) NOT NULL,
    debt_to_income_ratio DECIMAL(5, 2) NOT NULL,
    employer_name VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    decision_reason TEXT,
    decision_time_ms DECIMAL(8, 2),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decided_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS decision_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id VARCHAR(50) NOT NULL,
    stage VARCHAR(100) NOT NULL,
    outcome VARCHAR(100) NOT NULL,
    notes TEXT,
    performer VARCHAR(100) DEFAULT 'System Engine',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_id) REFERENCES loan_applications(app_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date VARCHAR(50) UNIQUE NOT NULL,
    submitted INTEGER NOT NULL DEFAULT 0,
    auto_approved INTEGER NOT NULL DEFAULT 0,
    auto_rejected INTEGER NOT NULL DEFAULT 0,
    manual_review INTEGER NOT NULL DEFAULT 0,
    final_approved INTEGER NOT NULL DEFAULT 0,
    final_rejected INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_loan_applications_app_id ON loan_applications(app_id);
CREATE INDEX IF NOT EXISTS idx_loan_applications_status ON loan_applications(status);
CREATE INDEX IF NOT EXISTS idx_decision_history_app_id ON decision_history(app_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
