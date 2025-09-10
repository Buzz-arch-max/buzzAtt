from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum

class ProfileType(str, enum.Enum):
    student = "student"
    lecturer = "lecturer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    matric_number = Column(String, nullable=True)
    department = Column(String)
    faculty = Column(String)
    hashed_password = Column(String)
    profile_type = Column(Enum(ProfileType))

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    course_name = Column(String)
    session_start = Column(DateTime)
    session_end = Column(DateTime)
    session_duration = Column(Integer)  # in seconds
    created_by = Column(Integer, ForeignKey("users.id"))

    attendances = relationship("Attendance", back_populates="session")

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime)
    ip_address = Column(String)

    session = relationship("AttendanceSession", back_populates="attendances")
