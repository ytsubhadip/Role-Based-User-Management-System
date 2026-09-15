from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, model_validator


class AdminUserRegistration(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: Literal["teacher", "student"]

    subject: str | None = None
    standard: str | None = None

    @model_validator(mode="after")

    def validate_role_fields(self):
        if self.role == "teacher":
            if not self.subject:
                raise ValueError(
                    "Subject is required for a teacher"
                )

            self.standard = None

        elif self.role == "student":
            if not self.standard:
                raise ValueError(
                    "Standard is required for a student"
                )

            self.subject = None

        return self


    model_config = {

            "json_schema_extra":{
                "example":{
                    "full_name":"coderPG",
                    "email":"local02299@gmail.com",
                    "role":"teacher",
                    "subject":"C",
                    "standard":None

                }
            }
    }