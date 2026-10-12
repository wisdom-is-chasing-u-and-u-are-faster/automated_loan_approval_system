from pydantic import BaseModel, EmailStr
from typing import Optional


class UserLoginRequest(BaseModel):
    email: Optional[str] = "student@university.edu"
    password: Optional[str] = "password123"
    role: Optional[str] = "student"


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    student_id: Optional[str] = None
    department: Optional[str] = None


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
