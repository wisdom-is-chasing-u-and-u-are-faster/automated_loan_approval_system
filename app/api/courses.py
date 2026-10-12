"""
Course Catalog & Enrollment Router.
"""
import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.db.database import execute_query, execute_one, execute_commit
from app.models.course import CourseCreateRequest, CourseResponse
from app.models.enrollment import EnrollmentRequest, EnrollmentResponse
from app.services.enrollment_service import register_student_for_course
from app.api.auth import get_current_user

router = APIRouter(tags=["courses"])


@router.get("/api/v1/courses")
def list_courses(department: Optional[str] = None, search: Optional[str] = None):
    query = """
    SELECT 
        c.id, c.code, c.title, c.department, c.credits, c.description,
        cs.id as section_id, cs.schedule, cs.room, cs.capacity, cs.enrolled_count,
        (cs.capacity - cs.enrolled_count) as available_seats,
        u.full_name as instructor
    FROM courses c
    LEFT JOIN course_sections cs ON c.id = cs.course_id
    LEFT JOIN faculty f ON cs.faculty_id = f.id
    LEFT JOIN users u ON f.user_id = u.id
    WHERE 1=1
    """
    params = []
    if department:
        query += " AND c.department = ?"
        params.append(department)
    if search:
        query += " AND (c.code LIKE ? OR c.title LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    rows = execute_query(query, tuple(params))
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "code": r["code"],
            "title": r["title"],
            "department": r["department"],
            "credits": r["credits"],
            "description": r["description"],
            "instructor": r["instructor"] or "Staff",
            "schedule": r["schedule"] or "TBD",
            "capacity": r["capacity"] or 30,
            "enrolled_count": r["enrolled_count"] or 0,
            "available_seats": max(0, (r["capacity"] or 30) - (r["enrolled_count"] or 0)),
            "is_enrolled": False
        })
    return {"courses": results}


@router.post("/api/v1/courses", status_code=201)
def create_course(req: CourseCreateRequest, user: dict = Depends(get_current_user)):
    course_id = f"crs-{uuid.uuid4().hex[:6]}"
    section_id = f"sec-{uuid.uuid4().hex[:6]}"

    execute_commit(
        "INSERT INTO courses (id, code, title, department, credits, description) VALUES (?, ?, ?, ?, ?, ?)",
        (course_id, req.code, req.title, req.department, req.credits, req.description)
    )

    execute_commit(
        "INSERT INTO course_sections (id, course_id, term, schedule, room, capacity, enrolled_count) VALUES (?, ?, 'Fall 2026', ?, ?, ?, 0)",
        (section_id, course_id, req.schedule, req.room, req.capacity)
    )

    return {"id": course_id, "code": req.code, "title": req.title, "message": "Course created successfully"}


@router.put("/api/v1/courses/{course_id}")
def update_course(course_id: str, req: CourseCreateRequest, user: dict = Depends(get_current_user)):
    execute_commit(
        "UPDATE courses SET code = ?, title = ?, department = ?, credits = ?, description = ? WHERE id = ?",
        (req.code, req.title, req.department, req.credits, req.description, course_id)
    )
    return {"id": course_id, "message": "Course updated successfully"}


@router.delete("/api/v1/courses/{course_id}")
def delete_course(course_id: str, user: dict = Depends(get_current_user)):
    execute_commit("DELETE FROM course_sections WHERE course_id = ?", (course_id,))
    execute_commit("DELETE FROM courses WHERE id = ?", (course_id,))
    return {"id": course_id, "message": "Course deleted successfully"}


@router.post("/api/v1/enrollments/register", response_model=EnrollmentResponse, status_code=201)
def register_course(req: EnrollmentRequest, user: dict = Depends(get_current_user)):
    # Find student ID
    student = execute_one("SELECT id FROM students WHERE user_id = ? OR id = ?", (user["id"], user["id"]))
    student_id = student["id"] if student else "stu-001"

    result = register_student_for_course(student_id, req.course_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Registration failed"))

    return EnrollmentResponse(**result)


@router.delete("/api/v1/enrollments/{enrollment_id}")
def drop_enrollment(enrollment_id: str, user: dict = Depends(get_current_user)):
    enr = execute_one("SELECT * FROM enrollments WHERE id = ?", (enrollment_id,))
    if enr:
        execute_commit("DELETE FROM enrollments WHERE id = ?", (enrollment_id,))
        execute_commit(
            "UPDATE course_sections SET enrolled_count = MAX(0, enrolled_count - 1) WHERE id = ?",
            (enr["section_id"],)
        )
    return {"message": "Enrollment dropped successfully"}
