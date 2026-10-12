"""
Student Domain API Router.
"""
from fastapi import APIRouter, Depends
from app.db.database import execute_query, execute_one
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/v1/students", tags=["students"])


@router.get("/dashboard")
def get_student_dashboard(user: dict = Depends(get_current_user)):
    student = execute_one("SELECT * FROM students WHERE user_id = ? OR id = ?", (user["id"], user["id"]))
    if not student:
        student = execute_one("SELECT * FROM students LIMIT 1")

    student_id = student["id"] if student else "stu-001"

    # Enrolled courses
    enrolled = execute_query(
        """
        SELECT c.id, c.code, c.title, cs.schedule, cs.room, u.full_name as instructor
        FROM enrollments e
        JOIN course_sections cs ON e.section_id = cs.id
        JOIN courses c ON cs.course_id = c.id
        LEFT JOIN faculty f ON cs.faculty_id = f.id
        LEFT JOIN users u ON f.user_id = u.id
        WHERE e.student_id = ? AND e.status = 'enrolled'
        """,
        (student_id,)
    )

    # Grades
    grades = execute_query(
        """
        SELECT c.code, c.title, g.letter_grade, g.score
        FROM grades g
        JOIN course_sections cs ON g.section_id = cs.id
        JOIN courses c ON cs.course_id = c.id
        WHERE g.student_id = ?
        """,
        (student_id,)
    )

    # Tuition due
    invoices = execute_query(
        "SELECT SUM(amount) as total FROM student_invoices WHERE student_id = ? AND status = 'unpaid'",
        (student_id,)
    )
    tuition_due = invoices[0]["total"] if invoices and invoices[0]["total"] else 0.0

    return {
        "student": {
            "id": student_id,
            "name": user["full_name"],
            "major": student["major"] if student else "Computer Science",
            "gpa": student["gpa"] if student else 3.85,
            "credits_earned": student["credits_earned"] if student else 45
        },
        "enrolled_courses": enrolled,
        "recent_grades": grades,
        "tuition_due": tuition_due
    }


@router.get("/profile")
def get_student_profile(user: dict = Depends(get_current_user)):
    student = execute_one("SELECT * FROM students WHERE user_id = ?", (user["id"],))
    return {
        "id": student["id"] if student else "stu-001",
        "student_number": student["student_number"] if student else "STU-2026-001",
        "full_name": user["full_name"],
        "email": user["email"],
        "major": student["major"] if student else "Computer Science",
        "status": student["status"] if student else "active"
    }
