"""
Tests for Concurrency Lock and Seat Limit Overselling Prevention.
Maps to AC: [ARCH-2617-AC5] The system prevents more students from enrolling in a course than there are available seats.
"""
import pytest
from app.db.database import execute_query, execute_one, execute_commit
from app.db.init_db import init_database
from app.services.enrollment_service import register_student_for_course


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_prevents_overselling_beyond_capacity():
    """Verify system strictly rejects enrollment when available seats reaches zero."""
    # Create test section with capacity = 1 and enrolled_count = 1
    execute_commit(
        "INSERT OR REPLACE INTO course_sections (id, course_id, term, schedule, room, capacity, enrolled_count) VALUES ('sec-test-full', 'crs-301', 'Fall 2026', 'TBD', 'TBD', 1, 1)"
    )

    # Attempt to enroll new student into full section
    res = register_student_for_course(student_id="stu-new-999", course_id="sec-test-full")

    assert res["success"] is False
    assert "full" in res["message"].lower() or "closed" in res["message"].lower()

    # Verify enrolled count was not incremented
    section = execute_one("SELECT enrolled_count, capacity FROM course_sections WHERE id = 'sec-test-full'")
    assert section["enrolled_count"] == 1
    assert section["enrolled_count"] <= section["capacity"]
