from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db

from app.routers.registration import registration_route
from app.routers.admin import router as admin_route
from app.pages.route import router as html_pages
from app.routers.login import login_route
from app.routers.otp_verification import otp_verify

# create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# configer static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")


# include routers
app.include_router(registration_route)
app.include_router(html_pages)
app.include_router(admin_route)
app.include_router(login_route)
app.include_router(otp_verify)

@app.get("/db-test")    
def database_test(db: Session = Depends(get_db)):

    db.execute( text("SELECT 1"))

    return {
        "database": "MySQL connected"
    }


