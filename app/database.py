from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get Database URL from environment variable or use default for local development
database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/buzzatt")

# Handle different URL formats
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Additional URL validation and cleanup
if not database_url or "://" not in database_url:
    raise ValueError("Invalid database URL format")

# Clean up any potential quote characters or whitespace
database_url = database_url.strip().strip('"\'')
SQLALCHEMY_DATABASE_URL = database_url

try:
    # Create the engine with some safety options
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Enable connection health checks
        pool_recycle=300,    # Recycle connections every 5 minutes
        connect_args={"connect_timeout": 30}  # Set connection timeout
    )
except Exception as e:
    print(f"Error creating database engine: {e}")
    print(f"Database URL format (sanitized): {SQLALCHEMY_DATABASE_URL.split('@')[0]}@[HIDDEN]")
    raise
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
