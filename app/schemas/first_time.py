from pydantic import BaseModel, Field


class VerifyOTPRequest(BaseModel):
    user_id: str
    otp: str = Field(..., min_length=6, max_length=6)


class ChangeTemporaryPasswordRequest(BaseModel):
    user_id: str
    new_password: str = Field(..., min_length=8, description="New secure password (at least 8 chars)")


class ResendOTPRequest(BaseModel):
    user_id: str