from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.user import User
from app.schemas.teacher import TeacherUpdateStudent
from app.core.dependencies import require_teacher

teacher_route = APIRouter(prefix="/teacher", tags=["Teacher"])


@teacher_route.get("/my-students")
def get_my_assigned_students(
    db: Session = Depends(get_db),
    current_teacher: User = Depends(require_teacher)
):
    # Task 5: Only view students that are explicitly assigned to them by the Admin
    students = db.query(User).filter(
        User.role == "student",
        User.teacher_id == current_teacher.id
    ).all()

    return [
        {
            "id": str(s.id),
            "full_name": s.full_name,
            "email": s.email,
            "standard": s.standard,
            "teacher_id": str(current_teacher.id)
        }
        for s in students
    ]


@teacher_route.get("/students/{student_id}")
def get_assigned_student_detail(
    student_id: str,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(require_teacher)
):
    try:
        student_uuid = uuid.UUID(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format.")

    student = db.query(User).filter(User.id == student_uuid, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # Task 5: Teacher cannot view unassigned students or students assigned to other teachers
    if student.teacher_id != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only view details of students explicitly assigned to you."
        )

    return {
        "id": str(student.id),
        "full_name": student.full_name,
        "email": student.email,
        "standard": student.standard,
        "teacher_name": current_teacher.full_name,
        "subject": current_teacher.subject
    }


@teacher_route.put("/students/{student_id}")
def update_assigned_student(
    student_id: str,
    data: TeacherUpdateStudent,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(require_teacher)
):
    try:
        student_uuid = uuid.UUID(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format.")

    student = db.query(User).filter(User.id == student_uuid, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # Task 5: Check assignment
    if student.teacher_id != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You can only update students explicitly assigned to you."
        )

    if data.full_name is not None and data.full_name.strip():
        student.full_name = data.full_name.strip()

    if data.standard is not None and data.standard.strip():
        student.standard = data.standard.strip()

    if data.email is not None and data.email != student.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing and existing.id != student.id:
            raise HTTPException(status_code=400, detail="Email is already used by another account.")
        student.email = str(data.email)

    db.commit()
    db.refresh(student)

    return {
        "status": "success",
        "message": f"Student '{student.full_name}' details updated successfully.",
        "student": {
            "id": str(student.id),
            "full_name": student.full_name,
            "email": student.email,
            "standard": student.standard
        }
    }


@teacher_route.delete("/students/{student_id}")
def delete_student_forbidden(
    student_id: str,
    current_teacher: User = Depends(require_teacher)
):
    # Task 5: Restrictions: A Teacher is not allowed to delete any student records.
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied: Teachers are not authorized to delete student records. Contact the administrator."
    )
