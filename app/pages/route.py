from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["HTML Pages"])

templates = Jinja2Templates(directory="templates")


@router.get("/")
def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html"
    )


@router.get("/login")
def login_page_alias(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html"
    )


@router.get("/registration")
def user_registration_page(request: Request):
    return templates.TemplateResponse(
        request,
        "userRegistrationForm.html"
    )


@router.get("/verify-otp")
def first_time_setup_page(request: Request):
    return templates.TemplateResponse(
        request,
        "first_time_setup.html"
    )


@router.get("/admin/dashboard")
def admin_dashboard_page(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/dashboard.html"
    )


@router.get("/admin/create-user")
def admin_create_user_page(request: Request):
    return templates.TemplateResponse(
        request,
        "AdminRegistrationForm.html"
    )


@router.get("/teacher/dashboard")
def teacher_dashboard_page(request: Request):
    return templates.TemplateResponse(
        request,
        "teacher/dashboard.html"
    )


@router.get("/student/dashboard")
def student_dashboard_page(request: Request):
    return templates.TemplateResponse(
        request,
        "student/dashboard.html"
    )