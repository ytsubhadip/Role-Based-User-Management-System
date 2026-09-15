import pytest
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.database import get_db, SessionLocal
from app.models.user import User

client = TestClient(app)


def test_db_test_endpoint():
    res = client.get("/db-test")
    assert res.status_code == 200
    assert res.json()["database"] == "MySQL connected"


def test_admin_login_and_full_access():
    # Login as seeded default admin
    login_res = client.post("/login", json={"email": "admin@school.com", "password": "Admin@123456"})
    assert login_res.status_code == 200, login_res.text
    login_data = login_res.json()
    assert login_data["status"] == "success"
    assert login_data["role"] == "admin"
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify admin can view all users
    users_res = client.get("/admin/users", headers=headers)
    assert users_res.status_code == 200
    assert isinstance(users_res.json(), list)


def test_self_registration_validation():
    # 1. Teacher missing subject should fail
    t_fail = client.post("/registration", json={
        "full_name": "Invalid Teacher",
        "email": f"fail_teacher_{uuid.uuid4().hex[:6]}@school.com",
        "password": "Password@123",
        "role": "teacher",
        "subject": ""
    })
    assert t_fail.status_code == 422

    # 2. Student missing standard should fail
    s_fail = client.post("/registration", json={
        "full_name": "Invalid Student",
        "email": f"fail_student_{uuid.uuid4().hex[:6]}@school.com",
        "password": "Password@123",
        "role": "student",
        "standard": ""
    })
    assert s_fail.status_code == 422

    # 3. Valid Teacher self-registration
    t_email = f"valid_teacher_{uuid.uuid4().hex[:6]}@school.com"
    t_ok = client.post("/registration", json={
        "full_name": "Valid Teacher",
        "email": t_email,
        "password": "Password@123",
        "role": "teacher",
        "subject": "Mathematics"
    })
    assert t_ok.status_code == 200
    assert t_ok.json()["role"] == "teacher"

    # 4. Valid Student self-registration
    s_email = f"valid_student_{uuid.uuid4().hex[:6]}@school.com"
    s_ok = client.post("/registration", json={
        "full_name": "Valid Student",
        "email": s_email,
        "password": "Password@123",
        "role": "student",
        "standard": "Grade 10"
    })
    assert s_ok.status_code == 200
    assert s_ok.json()["role"] == "student"


def test_admin_create_user_and_first_time_login_flow():
    # Admin login
    admin_login = client.post("/login", json={"email": "admin@school.com", "password": "Admin@123456"})
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin creates a student
    stu_email = f"new_stu_{uuid.uuid4().hex[:6]}@school.com"
    create_res = client.post("/admin/users", headers=admin_headers, json={
        "full_name": "New Enrolled Student",
        "email": stu_email,
        "role": "student",
        "standard": "Grade 9"
    })
    assert create_res.status_code == 200, create_res.text
    create_data = create_res.json()
    temp_pass = create_data["temporary_password"]
    user_id = create_data["user_id"]

    # First login with temporary password
    login_attempt = client.post("/login", json={"email": stu_email, "password": temp_pass})
    assert login_attempt.status_code == 200
    login_resp_data = login_attempt.json()
    assert login_resp_data["status"] == "temporary_password"
    assert login_resp_data["user_id"] == user_id

    # Check that temporary password user cannot access protected dashboard APIs before OTP & password change
    # Retrieve user directly from DB to inspect OTP code
    db = SessionLocal()
    user_row = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    assert user_row.is_temporary_password is True
    assert user_row.must_change_password is True
    assert user_row.otp_hash is not None

    # Test invalid OTP code
    bad_otp_res = client.post("/first-time/verify-otp", json={"user_id": user_id, "otp": "000000"})
    assert bad_otp_res.status_code == 400

    # Test verifying with correct OTP: generate and set known OTP
    from app.core.otp import hash_otp
    user_row.otp_hash = hash_otp("123456")
    db.commit()
    db.close()

    verify_res = client.post("/first-time/verify-otp", json={"user_id": user_id, "otp": "123456"})
    assert verify_res.status_code == 200

    # Now change temporary password to permanent
    new_secure_pass = "SecurePass@2026"
    change_res = client.post("/first-time/change-password", json={
        "user_id": user_id,
        "new_password": new_secure_pass
    })
    assert change_res.status_code == 200
    change_data = change_res.json()
    assert change_data["status"] == "success"

    # Now verify login with the new permanent password
    new_login = client.post("/login", json={"email": stu_email, "password": new_secure_pass})
    assert new_login.status_code == 200
    assert new_login.json()["status"] == "success"
    assert new_login.json()["role"] == "student"


def test_student_assignment_and_teacher_permissions():
    # Admin login
    admin_login = client.post("/login", json={"email": "admin@school.com", "password": "Admin@123456"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    # Admin creates Teacher A and Teacher B
    tA_email = f"teacher_a_{uuid.uuid4().hex[:6]}@school.com"
    tB_email = f"teacher_b_{uuid.uuid4().hex[:6]}@school.com"

    tA_res = client.post("/admin/users", headers=admin_headers, json={
        "full_name": "Teacher Alice",
        "email": tA_email,
        "role": "teacher",
        "subject": "Chemistry"
    })
    tA_id = tA_res.json()["user_id"]
    tA_temp_pass = tA_res.json()["temporary_password"]

    tB_res = client.post("/admin/users", headers=admin_headers, json={
        "full_name": "Teacher Bob",
        "email": tB_email,
        "role": "teacher",
        "subject": "History"
    })
    tB_id = tB_res.json()["user_id"]

    # Admin creates Student S1
    s1_email = f"student_s1_{uuid.uuid4().hex[:6]}@school.com"
    s1_res = client.post("/admin/users", headers=admin_headers, json={
        "full_name": "Student Charlie",
        "email": s1_email,
        "role": "student",
        "standard": "Grade 11"
    })
    s1_id = s1_res.json()["user_id"]
    s1_temp_pass = s1_res.json()["temporary_password"]

    # Set both Teacher Alice and Student Charlie to active verified users in DB for testing
    from app.core.security import hash_password
    db = SessionLocal()
    tA_user = db.query(User).filter(User.id == uuid.UUID(tA_id)).first()
    tA_user.is_temporary_password = False
    tA_user.must_change_password = False
    tA_user.email_verified = True
    tA_user.password = hash_password("TeacherA@123")

    s1_user = db.query(User).filter(User.id == uuid.UUID(s1_id)).first()
    s1_user.is_temporary_password = False
    s1_user.must_change_password = False
    s1_user.email_verified = True
    s1_user.password = hash_password("Student1@123")
    db.commit()
    db.close()

    # Assign Student Charlie to Teacher Alice
    assign_res = client.post("/admin/assign-student", headers=admin_headers, json={
        "student_id": s1_id,
        "teacher_id": tA_id
    })
    assert assign_res.status_code == 200

    # Log in as Teacher Alice
    tA_login = client.post("/login", json={"email": tA_email, "password": "TeacherA@123"})
    tA_headers = {"Authorization": f"Bearer {tA_login.json()['access_token']}"}

    # Teacher Alice views assigned students
    my_students_res = client.get("/teacher/my-students", headers=tA_headers)
    assert my_students_res.status_code == 200
    my_students = my_students_res.json()
    assert any(s["id"] == s1_id for s in my_students)

    # Teacher Alice updates Student Charlie's details (allowed)
    update_stu_res = client.put(f"/teacher/students/{s1_id}", headers=tA_headers, json={
        "full_name": "Charlie Updated",
        "standard": "Grade 11 - Honors"
    })
    assert update_stu_res.status_code == 200
    assert update_stu_res.json()["student"]["full_name"] == "Charlie Updated"

    # Teacher Alice tries to delete student (forbidden)
    del_res = client.delete(f"/teacher/students/{s1_id}", headers=tA_headers)
    assert del_res.status_code == 403

    # Student Charlie logs in and views profile
    s1_login = client.post("/login", json={"email": s1_email, "password": "Student1@123"})
    s1_headers = {"Authorization": f"Bearer {s1_login.json()['access_token']}"}

    profile_res = client.get("/student/my-profile", headers=s1_headers)
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert profile_data["student"]["full_name"] == "Charlie Updated"
    assert profile_data["assigned_teacher"]["full_name"] == "Teacher Alice"
    assert profile_data["assigned_teacher"]["subject"] == "Chemistry"

    # Student Charlie tries to edit own profile (forbidden)
    stu_edit_res = client.put("/student/my-profile", headers=s1_headers, json={"full_name": "Hacked"})
    assert stu_edit_res.status_code == 403

    # Student Charlie tries to access Teacher endpoint (forbidden)
    stu_access_teacher = client.get("/teacher/my-students", headers=s1_headers)
    assert stu_access_teacher.status_code == 403

    # Re-assign Student Charlie to Teacher Bob
    reassign_res = client.post("/admin/assign-student", headers=admin_headers, json={
        "student_id": s1_id,
        "teacher_id": tB_id
    })
    assert reassign_res.status_code == 200

    # Check that Teacher Alice no longer sees Student Charlie
    my_students_after = client.get("/teacher/my-students", headers=tA_headers).json()
    assert not any(s["id"] == s1_id for s in my_students_after)


def test_html_pages_render():
    pages = [
        "/",
        "/login",
        "/registration",
        "/verify-otp",
        "/admin/dashboard",
        "/admin/create-user",
        "/teacher/dashboard",
        "/student/dashboard"
    ]
    for page in pages:
        res = client.get(page)
        assert res.status_code == 200, f"Page {page} failed to render with status {res.status_code}"

