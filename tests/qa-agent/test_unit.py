"""
QA Persona v2 -- auto-generated tests
Service: app
Suite:   unit
Source:  test_strategy/plans/app__unit.json
Generated: 2024-07-18T15:00:00Z
"""

import pytest
from unittest.mock import patch, MagicMock, call
from fastapi import HTTPException

# Assuming the following imports based on the provided source code and plan
from app.api.auth import login
from app.api.courses import create_course, register_course
from app.models.user import UserLoginRequest
from app.models.course import CourseCreateRequest
from app.models.enrollment import EnrollmentRequest, EnrollmentResponse


def test_app_unit_001_login_authenticates_correctly():
    """Verify user login function authenticates correctly.

    test_id: app__unit__001
    target: login
    requirement_id: no requirement
    ac_ids: none
    """
    mock_user = {
        "id": "usr-123",
        "email": "student@university.edu",
        "full_name": "Test Student",
        "role": "student"
    }
    mock_token = "fake.jwt.token"

    with patch('app.api.auth.execute_one') as mock_execute_one, \
         patch('app.api.auth.create_token', return_value=mock_token) as mock_create_token, \
         patch('app.api.auth._resolve_user_profile', return_value=("stu-123", None)) as mock_resolve_profile:
        
        mock_execute_one.return_value = mock_user
        req = UserLoginRequest(email="student@university.edu", password="password123")
        
        response = login(req)

        mock_execute_one.assert_called_once_with("SELECT * FROM users WHERE email = ?", ("student@university.edu",))
        mock_create_token.assert_called_once_with(mock_user["id"], mock_user["email"], mock_user["role"])
        mock_resolve_profile.assert_called_once_with(mock_user)
        
        assert response.token == mock_token
        assert response.user.id == mock_user["id"]
        assert response.user.email == mock_user["email"]


def test_app_unit_002_create_course_logic():
    """Verify course creation logic.

    test_id: app__unit__002
    target: create_course
    requirement_id: no requirement
    ac_ids: none
    """
    with patch('app.api.courses.execute_commit') as mock_execute_commit, \
         patch('app.api.courses.uuid.uuid4') as mock_uuid:
        
        mock_uuid.return_value.hex = 'abcdef'
        course_req = CourseCreateRequest(
            code="CS101",
            title="Intro to CS",
            department="Computer Science",
            credits=3,
            schedule="MWF 10-11",
            room="Room 101",
            capacity=50
        )
        mock_user = {"id": "fac-001"}

        result = create_course(course_req, mock_user)

        assert mock_execute_commit.call_count == 2
        expected_calls = [
            call(
                "INSERT INTO courses (id, code, title, department, credits, description) VALUES (?, ?, ?, ?, ?, ?)",
                ('crs-abcdef', 'CS101', 'Intro to CS', 'Computer Science', 3, '')
            ),
            call(
                "INSERT INTO course_sections (id, course_id, term, schedule, room, capacity, enrolled_count) VALUES (?, ?, 'Fall 2026', ?, ?, ?, 0)",
                ('sec-abcdef', 'crs-abcdef', 'MWF 10-11', 'Room 101', 50)
            )
        ]
        mock_execute_commit.assert_has_calls(expected_calls, any_order=True)

        assert result == {
            "id": "crs-abcdef",
            "code": "CS101",
            "title": "Intro to CS",
            "message": "Course created successfully"
        }


def test_app_unit_003_register_course_logic():
    """Verify course registration logic.

    test_id: app__unit__003
    target: register_course
    requirement_id: no requirement
    ac_ids: none
    """
    mock_user = {"id": "usr-student", "email": "student@test.com", "role": "student"}
    mock_student = {"id": "stu-001"}
    enrollment_req = EnrollmentRequest(course_id="crs-101")

    # Success case
    with patch('app.api.courses.execute_one', return_value=mock_student) as mock_execute_one, \
         patch('app.api.courses.register_student_for_course') as mock_register_service:
        
        mock_service_result = {
            "success": True, 
            "message": "Successfully enrolled", 
            "enrollment_id": "enr-123",
            "course_id": "crs-101"
        }
        mock_register_service.return_value = mock_service_result

        response = register_course(enrollment_req, mock_user)

        mock_execute_one.assert_called_once_with("SELECT id FROM students WHERE user_id = ? OR id = ?", (mock_user["id"], mock_user["id"]))
        mock_register_service.assert_called_once_with(mock_student["id"], enrollment_req.course_id)
        assert isinstance(response, EnrollmentResponse)
        assert response.success is True
        assert response.enrollment_id == "enr-123"

    # Failure case (course not found)
    with patch('app.api.courses.execute_one', return_value=mock_student) as mock_execute_one, \
         patch('app.api.courses.register_student_for_course') as mock_register_service:

        mock_register_service.return_value = {"success": False, "message": "Course section not found"}

        with pytest.raises(HTTPException) as exc_info:
            register_course(enrollment_req, mock_user)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Course section not found"
