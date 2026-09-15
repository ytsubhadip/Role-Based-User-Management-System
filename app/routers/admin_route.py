from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app.models.user import User
from app.schemas.admin import (
    AdminUserCreation,
    AdminUserUpdate,
    AssignStudentRequest,
    BulkAssignStudentsRequest
)
from app.core.security import hash_password
from app.core.generator_password import generate_temporary_password
from app.core.email_service import send_temporary_password_email
from app.core.dependencies import require_admin

admin_route = APIRouter(prefix="/admin", tags=["Admin"])


@admin_route.post("/users")
def admin_create_user(
    user_data: AdminUserCreation,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    temporary_password = generate_temporary_password(12)

    teacher_id_uuid = None
    if user_data.role == "student" and user_data.teacher_id:
        try:
            teacher_id_uuid = uuid.UUID(user_data.teacher_id)
            teacher = db.query(User).filter(User.id == teacher_id_uuid, User.role == "teacher").first()
            if not teacher:
                raise HTTPException(status_code=400, detail="Selected teacher does not exist.")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid teacher ID format.")

    new_user = User(
        id=uuid.uuid4(),
        full_name=user_data.full_name,
        email=str(user_data.email),
        role=user_data.role,
        subject=user_data.subject if user_data.role == "teacher" else None,
        standard=user_data.standard if user_data.role == "student" else None,
        teacher_id=teacher_id_uuid,
        password=hash_password(temporary_password),
        email_verified=False,
        is_temporary_password=True,
        must_change_password=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # If new user is a teacher and student IDs were provided for assignment:
    if user_data.role == "teacher" and user_data.assigned_student_ids:
        for s_id_str in user_data.assigned_student_ids:
            try:
                s_uuid = uuid.UUID(s_id_str)
                stud = db.query(User).filter(User.id == s_uuid, User.role == "student").first()
                if stud:
                    stud.teacher_id = new_user.id
            except ValueError:
                continue
        db.commit()

    # Send temporary credentials via email
    send_temporary_password_email(
        receiver_email=new_user.email,
        full_name=new_user.full_name,
        temporary_password=temporary_password
    )

    return {
        "status": "success",
        "message": f"User '{new_user.full_name}' created successfully with a temporary password.",
        "user_id": str(new_user.id),
        "email": new_user.email,
        "role": new_user.role,
        "temporary_password": temporary_password
    }


@admin_route.get("/users")
def get_all_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    users = query.all()

    result = []
    for u in users:
        teacher_name = None
        if u.role == "student" and u.teacher_id:
            t = db.query(User).filter(User.id == u.teacher_id).first()
            if t:
                teacher_name = t.full_name

        result.append({
            "id": str(u.id),
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "subject": u.subject,
            "standard": u.standard,
            "teacher_id": str(u.teacher_id) if u.teacher_id else None,
            "teacher_name": teacher_name,
            "email_verified": u.email_verified,
            "is_temporary_password": u.is_temporary_password,
            "must_change_password": u.must_change_password
        })

    return result


@admin_route.get("/teachers")
def get_all_teachers(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    teachers = db.query(User).filter(User.role == "teacher").all()
    result = []
    for t in teachers:
        # Fetch assigned students
        students = db.query(User).filter(User.role == "student", User.teacher_id == t.id).all()
        result.append({
            "id": str(t.id),
            "full_name": t.full_name,
            "email": t.email,
            "subject": t.subject,
            "assigned_students_count": len(students),
            "assigned_students": [
                {
                    "id": str(s.id),
                    "full_name": s.full_name,
                    "email": s.email,
                    "standard": s.standard
                }
                for s in students
            ]
        })
    return result


@admin_route.get("/students")
def get_all_students(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    students = db.query(User).filter(User.role == "student").all()
    result = []
    for s in students:
        assigned_teacher = None
        if s.teacher_id:
            t = db.query(User).filter(User.id == s.teacher_id).first()
            if t:
                assigned_teacher = {
                    "id": str(t.id),
                    "full_name": t.full_name,
                    "email": t.email,
                    "subject": t.subject
                }
        result.append({
            "id": str(s.id),
            "full_name": s.full_name,
            "email": s.email,
            "standard": s.standard,
            "teacher_id": str(s.teacher_id) if s.teacher_id else None,
            "assigned_teacher": assigned_teacher
        })
    return result


@admin_route.get("/users/{user_id}")
def get_user_detail(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    u = db.query(User).filter(User.id == user_uuid).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found.")

    teacher_info = None
    if u.role == "student" and u.teacher_id:
        t = db.query(User).filter(User.id == u.teacher_id).first()
        if t:
            teacher_info = {"id": str(t.id), "full_name": t.full_name, "email": t.email, "subject": t.subject}

    assigned_students = []
    if u.role == "teacher":
        stus = db.query(User).filter(User.role == "student", User.teacher_id == u.id).all()
        assigned_students = [{"id": str(s.id), "full_name": s.full_name, "standard": s.standard, "email": s.email} for s in stus]

    return {
        "id": str(u.id),
        "full_name": u.full_name,
        "email": u.email,
        "role": u.role,
        "subject": u.subject,
        "standard": u.standard,
        "teacher_id": str(u.teacher_id) if u.teacher_id else None,
        "teacher": teacher_info,
        "assigned_students": assigned_students,
        "email_verified": u.email_verified,
        "is_temporary_password": u.is_temporary_password
    }


@admin_route.put("/users/{user_id}")
def admin_update_user(
    user_id: str,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if data.full_name is not None:
        user.full_name = data.full_name

    if data.email is not None and data.email != user.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Email is already used by another account.")
        user.email = str(data.email)

    if data.role is not None:
        user.role = data.role

    if data.subject is not None or user.role == "teacher":
        user.subject = data.subject
    if user.role != "teacher":
        user.subject = None

    if data.standard is not None or user.role == "student":
        user.standard = data.standard
    if user.role != "student":
        user.standard = None
        user.teacher_id = None

    # Handle student teacher_id update
    if user.role == "student" and data.teacher_id is not None:
        if data.teacher_id == "" or data.teacher_id is None:
            user.teacher_id = None
        else:
            try:
                t_uuid = uuid.UUID(data.teacher_id)
                t = db.query(User).filter(User.id == t_uuid, User.role == "teacher").first()
                if not t:
                    raise HTTPException(status_code=400, detail="Assigned teacher does not exist.")
                user.teacher_id = t_uuid
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid teacher ID format.")

    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": f"User '{user.full_name}' updated successfully.",
        "user": {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "subject": user.subject,
            "standard": user.standard,
            "teacher_id": str(user.teacher_id) if user.teacher_id else None
        }
    }


@admin_route.delete("/users/{user_id}")
def admin_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Admin cannot delete their own account.")

    # If deleting a teacher, remove assignments for their students
    if user.role == "teacher":
        db.query(User).filter(User.teacher_id == user.id).update({User.teacher_id: None})

    db.delete(user)
    db.commit()

    return {
        "status": "success",
        "message": f"User '{user.full_name}' deleted successfully."
    }


@admin_route.post("/assign-student")
def admin_assign_student(
    data: AssignStudentRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    try:
        student_uuid = uuid.UUID(data.student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format.")

    student = db.query(User).filter(User.id == student_uuid, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    if not data.teacher_id or data.teacher_id.strip() == "":
        student.teacher_id = None
        db.commit()
        return {"status": "success", "message": f"Student '{student.full_name}' is now unassigned."}

    try:
        teacher_uuid = uuid.UUID(data.teacher_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid teacher ID format.")

    teacher = db.query(User).filter(User.id == teacher_uuid, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    student.teacher_id = teacher.id
    db.commit()

    return {
        "status": "success",
        "message": f"Student '{student.full_name}' has been assigned to Teacher '{teacher.full_name}'."
    }


@admin_route.post("/teachers/{teacher_id}/assign-students")
def admin_bulk_assign_students_to_teacher(
    teacher_id: str,
    data: BulkAssignStudentsRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    try:
        teacher_uuid = uuid.UUID(teacher_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid teacher ID format.")

    teacher = db.query(User).filter(User.id == teacher_uuid, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    assigned_count = 0
    for s_id_str in data.student_ids:
        try:
            s_uuid = uuid.UUID(s_id_str)
            student = db.query(User).filter(User.id == s_uuid, User.role == "student").first()
            if student:
                student.teacher_id = teacher.id
                assigned_count += 1
        except ValueError:
            continue

    db.commit()
    return {
        "status": "success",
        "message": f"{assigned_count} students assigned to Teacher '{teacher.full_name}'."
    }
