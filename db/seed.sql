-- ==============================================================================
-- Enterprise Automatic Loan Approval System (ALAS) DML Seed Records
-- ==============================================================================

-- Seed Users (Demo password hashes for development testing)
INSERT OR IGNORE INTO users (user_id, full_name, email, hashed_password, role, status) VALUES
('USR-001', 'Alice Admin', 'alice.a@alas.com', 'demo_hash_admin', 'Administrator', 'Active'),
('USR-002', 'Bob Reviewer', 'bob.r@alas.com', 'demo_hash_reviewer', 'Reviewer', 'Active'),
('USR-003', 'Charlie Viewer', 'charlie.v@alas.com', 'demo_hash_auditor', 'Auditor', 'Active'),
('USR-004', 'Diana Developer', 'diana.d@alas.com', 'demo_hash_dev', 'Developer', 'Active');

-- Seed Loan Applications
INSERT OR IGNORE INTO loan_applications (app_id, applicant_name, dob, email, phone, address, loan_type, amount_requested, loan_term_months, credit_score, annual_income, debt_to_income_ratio, employer_name, status, decision_reason, decision_time_ms, submitted_at, decided_at) VALUES
('APP-2024-0815', 'John Doe', '1985-05-20', 'j.doe@example.com', '+1 (555) 123-4567', '123 Main St, Anytown, USA 12345', 'Personal', 10000.00, 36, 680, 75000.00, 35.0, 'Acme Corp', 'MANUAL_REVIEW', 'Credit score (680) below auto-approval threshold (700). Flagged for manual review.', 240.50, '2024-07-21 14:30:00', NULL),
('APP-2024-0814', 'Jane Smith', '1990-11-14', 'j.smith@example.com', '+1 (555) 234-5678', '456 Oak Ave, Metropolis, USA 54321', 'Auto', 25500.00, 48, 745, 92000.00, 22.0, 'Global Tech', 'APPROVED', 'High credit score (745) and low DTI (22.0%). Auto-approved.', 180.20, '2024-07-21 14:25:00', '2024-07-21 14:25:01'),
('APP-2024-0812', 'Michael Johnson', '1978-03-08', 'm.johnson@example.com', '+1 (555) 345-6789', '789 Pine Rd, Gotham, USA 98765', 'Personal', 15000.00, 36, 580, 48000.00, 52.0, 'Local Services', 'REJECTED', 'Credit score (580) below minimum cutoff (600) and high DTI (52.0%). Auto-rejected.', 195.10, '2024-07-21 14:10:00', '2024-07-21 14:10:01'),
('APP-2024-0811', 'Emily Davis', '1992-08-25', 'e.davis@example.com', '+1 (555) 456-7890', '321 Elm St, Star City, USA 13579', 'Mortgage', 250000.00, 360, 780, 145000.00, 28.0, 'FinCorp Global', 'APPROVED', 'Excellent credit tier (780) and low DTI (28.0%). Auto-approved.', 210.00, '2024-07-21 13:50:00', '2024-07-21 13:50:01');

-- Seed Decision History
INSERT OR IGNORE INTO decision_history (app_id, stage, outcome, notes, performer, timestamp) VALUES
('APP-2024-0815', 'Initial Submission', 'Received', 'Application received via Enterprise UI portal.', 'System Ingestion', '2024-07-21 14:30:01'),
('APP-2024-0815', 'Automated Check', 'Flagged for Review', 'Credit score below threshold (700) for instant approval.', 'Rules Engine', '2024-07-21 14:30:02'),
('APP-2024-0814', 'Initial Submission', 'Received', 'Application received via API Client.', 'System Ingestion', '2024-07-21 14:25:00'),
('APP-2024-0814', 'Automated Check', 'Auto-Approved', 'Credit score and DTI meet prime auto-approval criteria.', 'Rules Engine', '2024-07-21 14:25:01'),
('APP-2024-0812', 'Initial Submission', 'Received', 'Application received via Enterprise UI portal.', 'System Ingestion', '2024-07-21 14:10:00'),
('APP-2024-0812', 'Automated Check', 'Auto-Rejected', 'Credit score below 600 risk threshold.', 'Rules Engine', '2024-07-21 14:10:01');

-- Seed Daily Reporting Summary
INSERT OR IGNORE INTO daily_reports (report_date, submitted, auto_approved, auto_rejected, manual_review, final_approved, final_rejected) VALUES
('2024-07-21', 1204, 980, 182, 42, 1051, 153),
('2024-07-20', 1150, 950, 160, 40, 1010, 140),
('2024-07-19', 1180, 960, 175, 45, 1030, 150),
('2024-07-18', 1090, 910, 140, 40, 970, 120),
('2024-07-17', 1220, 1010, 170, 40, 1070, 150);
