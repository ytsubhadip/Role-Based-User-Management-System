from pydantic import BaseModel


class VerifyOTPRequest(BaseModel):
    user_id: str
    otp: str


class ChangeTemporaryPasswordRequest(BaseModel):
    user_id: str
    new_password: str