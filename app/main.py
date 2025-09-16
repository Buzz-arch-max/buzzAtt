from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, security
from .database import engine, get_db
from datetime import datetime, timedelta
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BuzzAtt API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Try to make a simple query
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.post("/auth/login", response_model=schemas.LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "matric_number": user.matric_number,
        "email": user.email,
        "profile_type": user.profile_type
    }

@app.post("/auth/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if user.profile_type == schemas.ProfileType.student and not user.matric_number:
        raise HTTPException(status_code=400, detail="Matric number required for students")

    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        matric_number=user.matric_number,
        department=user.department,
        faculty=user.faculty,
        profile_type=user.profile_type,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/lecturer/attendance/save-session", response_model=schemas.SessionResponse)
async def save_session_attendance(
    session: schemas.SessionCreate,
    db: Session = Depends(get_db)
):
    db_session = models.AttendanceSession(
        session_id=session.session_id,
        course_name=session.course_name,
        session_start=session.session_start,
        session_end=session.session_end,
        session_duration=session.session_duration
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    for student in session.students:
        student_user = db.query(models.User).filter(
            models.User.matric_number == student.matric_number
        ).first()
        
        if student_user:
            attendance = models.Attendance(
                session_id=db_session.id,
                student_id=student_user.id,
                timestamp=student.timestamp,
                ip_address=student.ip_address
            )
            db.add(attendance)

    db.commit()
    return {
        "success": True,
        "message": "Session attendance saved successfully",
        "saved_count": len(session.students)
    }

@app.get("/lecturer/attendance/sessions", response_model=dict)
async def get_sessions(
    course_name: str = None,
    from_date: datetime = None,
    to_date: datetime = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.AttendanceSession)
    
    if course_name:
        query = query.filter(models.AttendanceSession.course_name == course_name)
    if from_date:
        query = query.filter(models.AttendanceSession.session_start >= from_date)
    if to_date:
        query = query.filter(models.AttendanceSession.session_end <= to_date)

    sessions = query.all()
    
    # Get all attendances for these sessions
    session_list = []
    for session in sessions:
        attendances = db.query(models.Attendance).filter(
            models.Attendance.session_id == session.id
        ).join(models.User).all()
        
        student_list = []
        for attendance in attendances:
            student = db.query(models.User).filter(models.User.id == attendance.student_id).first()
            student_list.append({
                "matric_number": student.matric_number,
                "timestamp": attendance.timestamp,
                "ip_address": attendance.ip_address
            })
            
        session_list.append({
            "session_id": session.session_id,
            "course_name": session.course_name,
            "date": session.session_start.date(),
            "start_time": session.session_start,
            "end_time": session.session_end,
            "duration": session.session_duration,
            "total_students": len(student_list),
            "students": student_list
        })
    
    return {
        "sessions": session_list,
        "total_sessions": len(session_list)
    }
