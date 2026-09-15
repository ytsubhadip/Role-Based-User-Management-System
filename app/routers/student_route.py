from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models.user import User
from app.core.dependencies import require_student

student_route = APIRouter(prefix="/student", tags=["Student"])


@student_route.get("/my-profile")
def get_my_student_profile(
    db: Session = Depends(get_db),
    current_student: User = Depends(require_student)
):
    # Task 6: Student can only view their own personal profile details and the basic details of their assigned Teacher
    teacher_info = None
    if current_student.teacher_id:
        teacher = db.query(User).filter(User.id == current_student.teacher_id).first()
        if teacher:
            teacher_info = {
                "id": str(teacher.id),
                "full_name": teacher.full_name,
                "email": teacher.email,
                "subject": teacher.subject
            }

    return {
        "student": {
            "id": str(current_student.id),
            "full_name": current_student.full_name,
            "email": current_student.email,
            "role": current_student.role,
            "standard": current_student.standard,
            "email_verified": current_student.email_verified
        },
        "assigned_teacher": teacher_info
    }


@student_route.put("/my-profile")
@student_route.patch("/my-profile")
@student_route.put("/profile")
def student_update_forbidden(current_student: User = Depends(require_student)):
    # Task 6 Restrictions: A Student has read-only access. They are not allowed to update their own details (or anyone else's).
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied: Students have read-only access. All profile updates must be made by your Teacher or Administrator."
    )


@student_route.delete("/my-profile")
def student_delete_forbidden(current_student: User = Depends(require_student)):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied: Students cannot delete account records."
    )
