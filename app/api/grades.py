"""
Student Grades & GPA Calculation API Router.
"""
from fastapi import APIRouter, Depends
from app.db.database import execute_query, execute_one
from app.services.grade_service import calculate_student_gpa
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/v1/grades", tags=["grades"])


@router.get("/my-grades")
def get_my_grades(user: dict = Depends(get_current_user)):
    student = execute_one("SELECT id FROM students WHERE user_id = ? OR id = ?", (user["id"], user["id"]))
    student_id = student["id"] if student else "stu-001"

    stats = calculate_student_gpa(student_id)

    records = execute_query(
        """
        SELECT 
            c.code, c.title, c.credits, g.letter_grade, g.score,
            cs.term, e.status
        FROM enrollments e
        JOIN course_sections cs ON e.section_id = cs.id
        JOIN courses c ON cs.course_id = c.id
        LEFT JOIN grades g ON g.enrollment_id = e.id
        WHERE e.student_id = ?
        ORDER BY cs.term DESC
        """,
        (student_id,)
    )

    # Group by term
    terms_map = {}
    for r in records:
        term = r["term"] or "Fall 2026"
        if term not in terms_map:
            terms_map[term] = []
        terms_map[term].append({
            "code": r["code"],
            "title": r["title"],
            "credits": r["credits"],
            "letter_grade": r["letter_grade"] or "In Progress",
            "percentage": r["score"] or 0.0,
            "status": r["status"]
        })

    semesters = []
    for term, courses in terms_map.items():
        semesters.append({
            "term": term,
            "term_gpa": stats["gpa"],
            "courses": courses
        })

    return {
        "cumulative_gpa": stats["gpa"],
        "total_credits": stats["total_credits"],
        "semesters": semesters
    }
