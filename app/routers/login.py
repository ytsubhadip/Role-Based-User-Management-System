from fastapi import APIRouter, Request, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.schemas.login import UserLoginSchema
from app.database import get_db
from app.models.user import User
from app.core.security import verify_password
from app.core.email_service import send_otp_email

from app.core.otp import generate_otp, hash_otp, verify_otp

login_route = APIRouter( tags=["auth"])

@login_route.post("/login")
async def user_login(user_data: UserLoginSchema = Body(...),
db : Session=Depends(get_db) 
):

    user = (
        db.query(User)
        .filter(User.email  == str(user_data.email))
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email"
        )
    
    if not verify_password(user_data.password , user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )   

    # Temporary-password user
    if (user.is_temporary_password or user.must_change_password):   
        return{
            "status": "temporary_password",
            "message": "OTP verification and password change required",
            "user_id": user.id
        }
    
    # Email verification check
    if not user.email_verified:

        otp = generate_otp()
        user.otp_hash = hash_otp(otp)
        user.otp_expiration = datetime.utcnow() + timedelta(minutes=10)
        user.otp_attempts = 0   
    
        db.commit()

        send_otp_email(
            receiver_email=user.email,
            full_name=user.full_name,
            otp=otp
        )


        return {
            "status": "email_not_verified",
            "message": "Please verify your email first",
            "user_id": user.id
        }

    # Normal login response for now
    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }

    