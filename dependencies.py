from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

def get_db():
    from main import SessionLocal  # 延迟导入
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()