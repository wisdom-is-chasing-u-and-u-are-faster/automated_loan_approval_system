-- Smart Student Management System (SSMS) Relational Schema
-- Compatible with PostgreSQL 16 and SQLite fallback

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL, -- 'student', 'faculty', 'admin', 'registrar', 'bursar'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    student_number TEXT UNIQUE NOT NULL,
    major TEXT NOT NULL,
    gpa REAL DEFAULT 0.0,
    credits_earned INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS faculty (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    faculty_number TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    department TEXT NOT NULL,
    credits INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS course_sections (
    id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL REFERENCES courses(id),
    faculty_id TEXT REFERENCES faculty(id),
    term TEXT NOT NULL,
    schedule TEXT NOT NULL,
    room TEXT NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 30,
    enrolled_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS enrollments (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id),
    section_id TEXT NOT NULL REFERENCES course_sections(id),
    status TEXT DEFAULT 'enrolled', -- 'enrolled', 'dropped', 'completed'
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, section_id)
);

CREATE TABLE IF NOT EXISTS grades (
    id TEXT PRIMARY KEY,
    enrollment_id TEXT NOT NULL REFERENCES enrollments(id),
    student_id TEXT NOT NULL REFERENCES students(id),
    section_id TEXT NOT NULL REFERENCES course_sections(id),
    letter_grade TEXT NOT NULL,
    score REAL NOT NULL,
    submitted_by TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_invoices (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id),
    invoice_number TEXT UNIQUE NOT NULL,
    term TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT DEFAULT 'unpaid', -- 'unpaid', 'paid', 'pending', 'cancelled'
    due_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL REFERENCES student_invoices(id),
    description TEXT NOT NULL,
    amount REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS payment_records (
    id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL REFERENCES student_invoices(id),
    amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    stripe_session_id TEXT,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transcript_requests (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id),
    delivery_type TEXT NOT NULL,
    recipient_email TEXT NOT NULL,
    special_instructions TEXT,
    status TEXT DEFAULT 'completed', -- 'queued', 'processing', 'completed'
    download_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compliance_audit_logs (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actor_id TEXT NOT NULL,
    actor_name TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    ip_address TEXT,
    hash TEXT
);
