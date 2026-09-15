from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Literal, Optional


class UserRegistration(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: Literal["student", "teacher"]
    subject: Optional[str] = None
    standard: Optional[str] = None

    @model_validator(mode="after")
    def check_role(self):
        if self.role == "teacher":
            if not self.subject or not self.subject.strip():
                raise ValueError("Subject is required when registering as a Teacher.")
            self.standard = None
        elif self.role == "student":
            if not self.standard or not self.standard.strip():
                raise ValueError("Standard is required when registering as a Student.")
            self.subject = None
        return self