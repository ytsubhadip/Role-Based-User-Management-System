# app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.admin import AdminUserRegistration
from app.core.security import hash_password
from app.core.generator_password import generate_temporary_password
from app.core.email_service import send_temporary_password_email

router = APIRouter(
    prefix="/admin",
    tags=["auth"]
)


@router.post("/users")
def create_user_by_admin(
    user_data: AdminUserRegistration,
    db: Session = Depends(get_db),
    # current_admin=Depends(require_admin)
):
    existing_user = (
        db.query(User)
        .filter(User.email == str(user_data.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    temporary_password = generate_temporary_password()

    new_user = User(
        full_name=user_data.full_name,
        email=str(user_data.email),

        role=user_data.role,
        subject=user_data.subject,
        standard=user_data.standard,

        password=hash_password(temporary_password),

        email_verified=False,
        is_temporary_password=True,
        must_change_password=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_temporary_password_email(
        receiver_email=new_user.email,
        full_name=new_user.full_name,
        temporary_password=temporary_password
    )

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    }