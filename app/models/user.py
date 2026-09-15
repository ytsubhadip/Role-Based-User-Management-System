import uuid
from sqlalchemy import Column, Integer, String, Uuid, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


# User table schema supporting Admin, Teacher, and Student roles
class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # "admin", "teacher", "student"
    subject = Column(String(100), nullable=True)  # Applicable only to Teachers
    standard = Column(String(100), nullable=True)  # Applicable only to Students
    
    # Relationship to map Students to a specific Teacher
    teacher_id = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    email_verified = Column(Boolean, default=False, nullable=False)
    is_temporary_password = Column(Boolean, default=False, nullable=False)
    must_change_password = Column(Boolean, default=False, nullable=False)
    otp_hash = Column(String(255), nullable=True)
    otp_expiration = Column(DateTime, nullable=True)
    otp_attempts = Column(Integer, default=0, nullable=False)

    # Self-referential relationship
    teacher = relationship("User", remote_side=[id], foreign_keys=[teacher_id], backref="students")