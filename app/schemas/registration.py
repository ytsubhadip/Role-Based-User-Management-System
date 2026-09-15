from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Literal, Optional


class   UserRegistration(BaseModel):
    full_name : str = Field(..., min_length=2, max_length=100)
    email : EmailStr
    password : str = Field(...,min_length=8)
    role : Literal["student", "teacher"]
    subject : Optional[str] = None
    standard : Optional[str] = None
    
    @model_validator(mode="after")
    def check_role(self):

        if self.role == "teacher" and not self.subject:
            raise  ValueError("Teacher needs  subject")

        if self.role == "student"  and not self.standard:
            raise ValueError("Student needs standard")

        return self