# app/apps/auth/router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime


from app.schemas.first_time import VerifyOTPRequest
from app.core.otp import verify_otp
from app.database import get_db
from app.models.user import User

otp_verify = APIRouter()

@otp_verify.post("/first-time/verify-otp")
def verify_first_time_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == data.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not user.otp_hash or not user.otp_expiration:
        raise HTTPException(
            status_code=400,
            detail="OTP not found. Please request a new OTP"
        )

    if datetime.utcnow() > user.otp_expiration:
        raise HTTPException(
            status_code=400,
            detail="OTP has expired"
        )

    if user.otp_attempts >= 5:
        raise HTTPException(
            status_code=429,
            detail="Too many incorrect attempts"
        )

    if not verify_otp(data.otp, user.otp_hash):
        user.otp_attempts += 1
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    user.email_verified = True
    user.otp_hash = None
    user.otp_expiration = None
    us