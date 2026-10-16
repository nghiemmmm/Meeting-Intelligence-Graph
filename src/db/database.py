import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Kiểm tra nếu đang chạy trên Vercel Serverless (chỉ cho phép ghi vào thư mục /tmp)
if os.environ.get("VERCEL"):
    DATA_DIR = "/tmp/data"
else:
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

os.makedirs(DATA_DIR, exist_ok=True)

SQLITE_FILE_PATH = os.path.join(DATA_DIR, "meetings.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_FILE_PATH}"

# connect_args={"check_same_thread": False} bắt buộc cho SQLite trong FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency cung cấp db session cho FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Khởi tạo toàn bộ các bảng trong SQLite nếu chưa tồn tại"""
    from src.db import models
    Base.metadata.create_all(bind=engine)
