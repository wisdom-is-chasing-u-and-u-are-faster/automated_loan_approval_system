"""
Grade management service with GPA computation and bulk async grade submission.
"""
import uuid
from typing import List, Dict, Any
from app.db.database import execute_query, execute_one, execute_commit

GRADE_POINTS = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "F": 0.0
}


def calculate_student_gpa(student_id: str) -> dict:
    """Calculates student cumulative GPA and total earned credits."""
    records = execute_query(
        """
        SELECT g.letter_grade, c.credits
        FROM grades g
        JOIN course_sections cs ON g.section_id = cs.id
        JOIN courses c ON cs.course_id = c.id
        WHERE g.student_id = ?
        """,
        (student_id,)
    )

    total_points = 0.0
    total_credits = 0

    for r in records:
        letter = r["letter_grade"].upper()
        credits = r["credits"]
        points = GRADE_POINTS.get(letter, 0.0)
        total_points += (points * credits)
        total_credits += credits

    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    return {"gpa": gpa, "total_credits": total_credits}


def process_bulk_grades(course_id: str, faculty_id: str, grades: List[Dict[str, Any]]) -> int:
    """Processes bulk grade submission asynchronously."""
    section = execute_one(
        "SELECT id FROM course_sections WHERE course_id = ? OR id = ?",
        (course_id, course_id)
    )
    if not section:
        return 0

    section_id = section["id"]
    processed = 0

    for item in grades:
        student_id = item["student_id"]
        letter = item["letter_grade"]
        score = item["score"]

        # Ensure enrollment exists
        enrollment = execute_one(
            "SELECT id FROM enrollments WHERE student_id = ? AND section_id = ?",
            (student_id, section_id)
        )
        enrollment_id = enrollment["id"] if enrollment else f"enr-auto-{uuid.uuid4().hex[:6]}"

        # Upsert grade
        existing_grade = execute_one(
            "SELECT id FROM grades WHERE student_id = ? AND section_id = ?",
            (student_id, section_id)
        )

        if existing_grade:
            execute_commit(
                "UPDATE grades SET letter_grade = ?, score = ?, submitted_by = ? WHERE id = ?",
                (letter, score, faculty_id, existing_grade["id"])
            )
        else:
            execute_commit(
                "INSERT INTO grades (id, enrollment_id, student_id, section_id, letter_grade, score, submitted_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"grd-{uuid.uuid4().hex[:8]}", enrollment_id, student_id, section_id, letter, score, faculty_id)
            )

        # Recalculate student GPA
        stats = calculate_student_gpa(student_id)
        execute_commit(
            "UPDATE students SET gpa = ?, credits_earned = ? WHERE id = ?",
            (stats["gpa"], stats["total_credits"], student_id)
        )
        processed += 1

    return processed
