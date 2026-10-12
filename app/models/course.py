from pydantic import BaseModel
from typing import Optional


class CourseCreateRequest(BaseModel):
    code: str
    title: str
    department: str
    credits: int
    capacity: int = 30
    instructor: Optional[str] = None
    schedule: Optional[str] = "Mon/Wed 10:00 AM - 11:30 AM"
    room: Optional[str] = "Hall 101"
    description: Optional[str] = ""


class CourseResponse(BaseModel):
    id: str
    code: str
    title: str
    department: str
    credits: int
    instructor: Optional[str] = "Staff"
    schedule: Optional[str] = "TBD"
    capacity: int
    enrolled_count: int
    available_seats: int
    is_enrolled: bool = False
