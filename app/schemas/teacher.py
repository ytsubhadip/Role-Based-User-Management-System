from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class TeacherUpdateStudent(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    standard: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
