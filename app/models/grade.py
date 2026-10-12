from pydantic import BaseModel
from typing import List, Optional


class SingleGradeSubmission(BaseModel):
    student_id: str
    letter_grade: str
    score: float


class BulkGradeSubmissionRequest(BaseModel):
    course_id: str
    grades: List[SingleGradeSubmission]


class BulkGradeSubmissionResponse(BaseModel):
    success: bool
    message: str
    processed_records: int
