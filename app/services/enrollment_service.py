"""
Enrollment service with concurrency control and seat limit enforcement.
"""
import uuid
import datetime
from app.db.database import execute_query, execute_one, execute_commit
from app.services.concurrency_lock import acquire_enrollment_lock


def register_student_for_course(student_id: str, course_id: str) -> dict:
    """
    Registers a student for a course section.
    Enforces concurrency lock to prevent overselling beyond capacity.
    """
    # 1. Find section for course
    section = execute_one(
        "SELECT id, capacity, enrolled_count FROM course_sections WHERE course_id = ? OR id = ?",
        (course_id, course_id)
    )
    if not section:
        return {"success": False, "message": "Course section not found"}

    section_id = section["id"]

    # 2. Acquire lock for section
    with acquire_enrollment_lock(section_id):
        # Re-fetch current state inside lock
        current_section = execute_one(
            "SELECT capacity, enrolled_count FROM course_sections WHERE id = ?",
            (section_id,)
        )
        if not current_section:
            return {"success": False, "message": "Course section not found"}

        capacity = current_section["capacity"]
        enrolled_count = current_section["enrolled_count"]

        # 3. Check duplicate enrollment
        existing = execute_one(
            "SELECT id FROM enrollments WHERE student_id = ? AND section_id = ? AND status = 'enrolled'",
            (student_id, section_id)
        )
        if existing:
            return {"success": False, "message": "Already enrolled in this course section"}

        # 4. Check available seats
        if enrolled_count >= capacity:
            return {
                "success": False,
                "message": f"Section is full (Capacity: {capacity}/{capacity}). Registration closed."
            }

        # 5. Create enrollment
        enrollment_id = f"enr-{uuid.uuid4().hex[:8]}"
        execute_commit(
            "INSERT INTO enrollments (id, student_id, section_id, status) VALUES (?, ?, ?, 'enrolled')",
            (enrollment_id, student_id, section_id)
        )

        # 6. Increment enrolled count
        execute_commit(
            "UPDATE course_sections SET enrolled_count = enrolled_count + 1 WHERE id = ?",
            (section_id,)
        )

        # 7. Record audit log
        audit_id = f"aud-{uuid.uuid4().hex[:8]}"
        execute_commit(
            "INSERT INTO compliance_audit_logs (id, actor_id, actor_name, action, entity_type, entity_id) VALUES (?, ?, 'Student', 'ENROLL_COURSE', 'CourseSection', ?)",
            (audit_id, student_id, section_id)
        )

        return {
            "success": True,
            "message": "Successfully enrolled in course",
            "enrollment_id": enrollment_id,
            "course_id": course_id,
            "enrolled_at": datetime.datetime.utcnow().isoformat()
        }
