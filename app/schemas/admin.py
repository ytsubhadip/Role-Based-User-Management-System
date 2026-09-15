from typing import Literal, Optional, List
from pydantic import BaseModel, EmailStr, Field, model_validator


class AdminUserCreation(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: Literal["teacher", "student"]
    subject: Optional[str] = None
    standard: Optional[str] = None
    # If creating a teacher, optional list of student IDs to immediately assign
    assigned_student_ids: Optional[List[str]] = None
    # If creating a student, optional teacher ID to immediately assign
    teacher_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_role_fields(self):
        if self.role == "teacher":
            if not self.subject or not self.subject.strip():
                raise ValueError("Subject is required for a Teacher.")
            self.standard = None
            self.teacher_id = None
        elif self.role == "student":
            if not self.standard or not self.standard.strip():
                raise ValueError("Standard is required for a Student.")
            self.subject = None
            self.assigned_student_ids = None
        return self


class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[Literal["teacher", "student", "admin"]] = None
    subject: Optional[str] = None
    standard: Optional[str] = None
    teacher_id: Optional[str] = None


class AssignStudentRequest(BaseModel):
    student_id: str
    teacher_id: Optional[str] = None  # None/empty string means unassign


class BulkAssignStudentsRequest(BaseModel):
    teacher_id: str
    student_ids: List[str]