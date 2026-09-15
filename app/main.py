from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
import os

from app.database import get_db, init_db
from app.routers.auth_route import auth_route
from app.routers.admin_route import admin_route
from app.routers.teacher_route import teacher_route
from app.routers.student_route import student_route
from app.pages.route import router as html_pages

# Initialize database schema and auto-seed admin if needed
init_db()

app = FastAPI(
    title="Role-Based User Management System",
    description="Enterprise RBAC system supporting Admin, Teacher, and Student workflows.",
    version="1.0.0"
)

# Static files
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API Routers
app.include_router(auth_route)
app.include_router(admin_route)
app.include_router(teacher_route)
app.include_router(student_route)

# Include HTML Page Routers
app.include_router(html_pages)


@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "MySQL connected"}
