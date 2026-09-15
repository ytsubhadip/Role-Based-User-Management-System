from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.orm import Session


from app.database import get_db 
from app.models.user import User
from app.schemas.registration import UserRegistration
from app.core.security import hash_password

registration_route = APIRouter(tags=["auth"])

@registration_route.post("/registration")
async def user_registration(
    data:UserRegistration =  Body(...),
    db:Session = Depends(get_db)
    ):

    # check if email already exists
    existing_user  = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="email already registered"
        )

    # password hashing
    hased_password = hash_password(
        data.password
    )   

    new_user = User(
        full_name =data.full_name,
        email = data.email,
        password = hased_password,
        role = data.role,
        subject = data.subject,
        standard = data.standard
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration successful",
        "user_id": new_user.id,
        "email": new_user.email
    }



    