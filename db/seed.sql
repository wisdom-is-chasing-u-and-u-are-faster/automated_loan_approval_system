-- Baseline Seed Data for Smart Student Management System (SSMS)

-- 1. Users
INSERT OR IGNORE INTO users (id, email, password_hash, full_name, role) VALUES
('usr-student-01', 'student@university.edu', 'mock_dev_hash_student_123', 'Alex Rivers', 'student'), -- pragma: allowlist secret
('usr-faculty-01', 'faculty@university.edu', 'mock_dev_hash_faculty_123', 'Dr. Eleanor Vance', 'faculty'), -- pragma: allowlist secret
('usr-admin-01', 'admin@university.edu', 'mock_dev_hash_admin_123', 'Sarah Jenkins (Registrar)', 'admin'); -- pragma: allowlist secret

-- 2. Students & Faculty Profiles
INSERT OR IGNORE INTO students (id, user_id, student_number, major, gpa, credits_earned, status) VALUES
('stu-001', 'usr-student-01', 'STU-2026-001', 'Computer Science', 3.85, 45, 'active');

INSERT OR IGNORE INTO faculty (id, user_id, faculty_number, department, title) VALUES
('fac-001', 'usr-faculty-01', 'FAC-101', 'Computer Science', 'Associate Professor');

-- 3. Courses
INSERT OR IGNORE INTO courses (id, code, title, department, credits, description) VALUES
('crs-101', 'CS101', 'Introduction to Computer Science', 'Computer Science', 4, 'Foundations of programming, algorithms, and data structures.'),
('crs-201', 'CS201', 'Data Structures & Algorithms', 'Computer Science', 4, 'Advanced data representations, sorting, graph algorithms, and complexity analysis.'),
('crs-301', 'CS301', 'Database Systems & Architecture', 'Computer Science', 3, 'Relational models, SQL, indexing, concurrency control, and transactions.'),
('crs-401', 'MATH201', 'Discrete Mathematics', 'Mathematics', 3, 'Logic, set theory, combinatorics, graph theory, and proof methods.'),
('crs-501', 'BIO101', 'General Biology & Lab', 'Biological Sciences', 4, 'Cellular biology, genetics, and ecological systems.');

-- 4. Course Sections
INSERT OR IGNORE INTO course_sections (id, course_id, faculty_id, term, schedule, room, capacity, enrolled_count) VALUES
('sec-101', 'crs-101', 'fac-001', 'Fall 2026', 'Mon/Wed 10:00 AM - 11:30 AM', 'Turing Hall 101', 30, 2),
('sec-201', 'crs-201', 'fac-001', 'Fall 2026', 'Tue/Thu 01:00 PM - 02:30 PM', 'Hopper Lab 204', 25, 1),
('sec-301', 'crs-301', 'fac-001', 'Fall 2026', 'Mon/Wed 02:00 PM - 03:15 PM', 'Knuth Hall 302', 2, 1);

-- 5. Enrollments
INSERT OR IGNORE INTO enrollments (id, student_id, section_id, status) VALUES
('enr-001', 'stu-001', 'sec-101', 'completed'),
('enr-002', 'stu-001', 'sec-201', 'enrolled');

-- 6. Grades
INSERT OR IGNORE INTO grades (id, enrollment_id, student_id, section_id, letter_grade, score, submitted_by) VALUES
('grd-001', 'enr-001', 'stu-001', 'sec-101', 'A', 94.5, 'fac-001');

-- 7. Invoices & Items
INSERT OR IGNORE INTO student_invoices (id, student_id, invoice_number, term, amount, status, due_date) VALUES
('inv-001', 'stu-001', 'INV-2026-F-001', 'Fall 2026', 4250.00, 'unpaid', '2026-11-15'),
('inv-002', 'stu-001', 'INV-2026-S-001', 'Spring 2026', 4000.00, 'paid', '2026-04-15');

INSERT OR IGNORE INTO invoice_items (id, invoice_id, description, amount) VALUES
('item-001', 'inv-001', 'Fall 2026 Tuition (11 Credits)', 3850.00),
('item-002', 'inv-001', 'Technology & Lab Fee', 250.00),
('item-003', 'inv-001', 'Campus Activity Fee', 150.00),
('item-004', 'inv-002', 'Spring 2026 Full Tuition', 4000.00);

-- 8. Payment Records
INSERT OR IGNORE INTO payment_records (id, invoice_id, amount, payment_method, stripe_session_id, status) VALUES
('pay-001', 'inv-002', 4000.00, 'Credit Card (Stripe)', 'cs_test_mock_spring_2026', 'completed');

-- 9. Audit Logs
INSERT OR IGNORE INTO compliance_audit_logs (id, actor_id, actor_name, action, entity_type, entity_id, ip_address, hash) VALUES
('aud-001', 'usr-admin-01', 'Sarah Jenkins (Registrar)', 'SYSTEM_INIT', 'System', 'ssms-core', '127.0.0.1', 'genesis_audit_log_hash_001'); -- pragma: allowlist secret
