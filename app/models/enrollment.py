from pydantic import BaseModel
from typing import Optional


class EnrollmentRequest(BaseModel):
    course_id: str


class EnrollmentResponse(BaseModel):
    success: bool
    message: str
    enrollment_id: Optional[str] = None
    course_id: Optional[str] = None
    enrolled_at: Optional[str] = None
