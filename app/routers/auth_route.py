from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid

from app.database import get_db
from app.models.user import User
from app.schemas.login import UserLoginSchema
from app.schemas.registration import UserRegistration
from app.schemas.first_time import VerifyOTPRequest, ChangeTemporaryPasswordRequest, ResendOTPRequest
from app.core.security import hash_password, verify_password
from app.core.otp import generate_otp, hash_otp, verify_otp
from app.core.email_service import send_otp_email
from app.core.jwt import create_access_token
from app.core.dependencies import get_current_user

auth_route = APIRouter(tags=["Authentication"])


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@auth_route.post("/login")
def user_login(
    response: Response,
    user_data: UserLoginSchema,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Document Task 3: First-Time Login Flow for temporary password
    if user.is_temporary_password or user.must_change_password:
        otp = generate_otp()
        user.otp_hash = hash_otp(otp)
        user.otp_expiration = utc_now() + timedelta(minutes=10)
        user.otp_attempts = 0
        db.commit()

        send_otp_email(
            receiver_email=user.email,
            full_name=user.full_name,
            otp=otp
        )

        return {
            "status": "temporary_password",
            "message": "First-time login detected. An OTP has been sent to your email. Please verify OTP and change your temporary password.",
            "user_id": str(user.id),
            "email": user.email
        }

    # Normal email verification check
    if not user.email_verified:
        otp = generate_otp()
        user.otp_hash = hash_otp(otp)
        user.otp_expiration = utc_now() + timedelta(minutes=10)
        user.otp_attempts = 0
        db.commit()


        send_otp_email(
            receiver_email=user.email,
            full_name=user.full_name,
            otp=otp
        )

        return {
            "status": "email_not_verified",
            "message": "Please verify your email address. An OTP has been sent.",
            "user_id": str(user.id),
            "email": user.email
        }

    # Standard authenticated login
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email, "name": user.full_name}
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        max_age=86400
    )

    return {
        "status": "success",
        "message": "Login successful.",
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user": {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "subject": user.subject,
            "standard": user.standard
        }
    }


@auth_route.post("/first-time/verify-otp")
def verify_first_time_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    try:
        user_uuid = uuid.UUID(data.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if not user.otp_hash or not user.otp_expiration:
        raise HTTPException(
            status_code=400,
            detail="No pending OTP request found. Please request a new OTP."
        )

    if utc_now() > user.otp_expiration:
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new OTP.")

    if user.otp_attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many incorrect OTP attempts. Please request a new one.")

    if not verify_otp(data.otp, user.otp_hash):
        user.otp_attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid OTP code.")

    # OTP verified! Mark email as verified and clear OTP hash
    user.email_verified = True
    user.otp_hash = None
    user.otp_expiration = None
    user.otp_attempts = 0
    db.commit()

    return {
        "status": "success",
        "message": "OTP verified successfully. You can now set your new password.",
        "user_id": str(user.id)
    }


@auth_route.post("/first-time/resend-otp")
def resend_first_time_otp(
    data: ResendOTPRequest,
    db: Session = Depends(get_db)
):
    try:
        user_uuid = uuid.UUID(data.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    otp = generate_otp()
    user.otp_hash = hash_otp(otp)
    user.otp_expiration = utc_now() + timedelta(minutes=10)

    user.otp_attempts = 0
    db.commit()

    send_otp_email(receiver_email=user.email, full_name=user.full_name, otp=otp)

    return {
        "status": "success",
        "message": "A new OTP code has been sent to your email."
    }


@auth_route.post("/first-time/change-password")
def change_temporary_password(
    response: Response,
    data: ChangeTemporaryPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        user_uuid = uuid.UUID(data.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if not user.email_verified:
        raise HTTPException(status_code=400, detail="Please verify your OTP before changing password.")

    if not user.is_temporary_password and not user.must_change_password:
        raise HTTPException(status_code=400, detail="User does not have a pending temporary password reset.")

    # Update to new secure password
    user.password = hash_password(data.new_password)
    user.is_temporary_password = False
    user.must_change_password = False
    user.otp_hash = None
    user.otp_expiration = None
    user.otp_attempts = 0
    db.commit()

    # Create access token and set cookie so user is now logged in seamlessly
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email, "name": user.full_name}
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        max_age=86400
    )

    return {
        "status": "success",
        "message": "Password changed successfully. You can now access your dashboard.",
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": str(user.id)
    }


@auth_route.post("/registration")
def user_self_registration(
    data: UserRegistration,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    new_user = User(
        id=uuid.uuid4(),
        full_name=data.full_name,
        email=str(data.email),
        password=hash_password(data.password),
        role=data.role,
        subject=data.subject if data.role == "teacher" else None,
        standard=data.standard if data.role == "student" else None,
        email_verified=True,
        is_temporary_password=False,
        must_change_password=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "message": f"Registration successful as {new_user.role}. You may now log in.",
        "user_id": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role
    }


@auth_route.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": str(current_user.id),
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "subject": current_user.subject,
        "standard": current_user.standard,
        "teacher_id": str(current_user.teacher_id) if current_user.teacher_id else None
    }


@auth_route.post("/logout")
def user_logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"status": "success", "message": "Successfully logged out."}