# BuzzAtt Backend API

A FastAPI-based backend for the BuzzAtt attendance management system.

## Deployment on Render

1. Fork or push this repository to your GitHub account.

2. Go to [render.com](https://render.com) and create an account if you haven't already.

3. Click on "New +" and select "Web Service".

4. Connect your GitHub repository.

5. Configure the Web Service:
   - Name: buzzatt-api (or your preferred name)
   - Environment: Python
   - Region: Choose the closest to your users
   - Branch: main
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. Add Environment Variables:
   - `SECRET_KEY`: Generate a secure random string
   - `DATABASE_URL`: This will be automatically added when you create the database

7. Click "Create Web Service"

8. Create a PostgreSQL database:
   - Go to "New +" again and select "PostgreSQL"
   - Name: buzzatt-db
   - Plan: Free
   - Region: Same as your web service

9. Once both are created, Render will automatically connect them using the DATABASE_URL environment variable.

Your API will be available at: `https://your-service-name.onrender.com`

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL:
- The database should be created and running
- Update the DATABASE_URL in .env if needed

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc UI

## Environment Variables

Create a `.env` file with:
- DATABASE_URL: PostgreSQL connection string
- SECRET_KEY: Secret key for JWT tokens
- ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time

## Available Endpoints

### Authentication
- POST /auth/login/ - Login user
- POST /auth/register/ - Register new user

### Attendance Management (Lecturer Only)
- POST /lecturer/attendance/save-session - Save attendance session
- GET /lecturer/attendance/sessions - Get sessions history
- POST /lecturer/attendance/sync - Sync offline sessions
