from fastapi import APIRouter, Body, HTTPException, Depends, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=["HTML Pages"])

templates = Jinja2Templates(directory="templates") 
@router.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        request=request
    )

@router.get("/registration")
def user_registration(request: Request):
    return templates.TemplateResponse(
        name="userRegistrationForm.html",
        request=request
    )

    
@router.get("/admin/registration")
def admin_registration(request: Request):
    return templates.TemplateResponse(
        name="AdminRegistrationForm.html",
        request=request
    )
    