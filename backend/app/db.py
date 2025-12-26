from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# PostgreSQL 配置
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:<your_password>@postgres.railway.internal:5432/railway')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 

__all__ = ["Base", "init_db", "get_db"]
