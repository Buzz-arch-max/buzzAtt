from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum

class ProfileType(str, Enum):
    student = "student"
    lecturer = "lecturer"

class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    department: str
    faculty: str

class UserCreate(UserBase):
    password: str
    profile_type: ProfileType
    matric_number: Optional[str] = None

class User(UserBase):
    id: int
    profile_type: ProfileType
    matric_number: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    profile: dict = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    matric_number: str | None = None
    email: str
    profile_type: ProfileType

class StudentAttendance(BaseModel):
    matric_number: str
    timestamp: datetime
    ip_address: str

class SessionCreate(BaseModel):
    session_id: str
    course_name: str
    session_start: datetime
    session_end: datetime
    session_duration: int
    students: List[StudentAttendance]

class SessionResponse(BaseModel):
    success: bool
    message: str
    saved_count: int

class Session(BaseModel):
    session_id: str
    course_name: str
    date: datetime
    start_time: datetime
    end_time: datetime
    duration: int
    total_students: int
    students: List[StudentAttendance]

    class Config:
        from_attributes = True
