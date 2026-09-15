from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models.user import User
    from app.core.security import hash_password

    # Create tables if not present
    Base.metadata.create_all(bind=engine)

    # Check and add teacher_id column if missing in MySQL
    inspector = inspect(engine)
    if "users" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("users")]
        with engine.begin() as conn:
            if "teacher_id" not in columns:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN teacher_id CHAR(32) NULL"))
                    conn.execute(text("ALTER TABLE users ADD CONSTRAINT fk_user_teacher FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL"))
                except Exception as e:
                    print(f"Migration note for teacher_id: {e}")

    # Seed initial Admin if not exists
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.role == "admin").first()
        if not admin_user:
            default_admin = User(
                id=uuid.uuid4(),
                full_name="System Administrator",
                email="admin@school.com",
                password=hash_password("Admin@123456"),
                role="admin",
                email_verified=True,
                is_temporary_password=False,
                must_change_password=False
            )
            db.add(default_admin)
            db.commit()
            print("Default admin created: admin@school.com / Admin@123456")
    finally:
        db.close()