from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import os

# SQLAlchemy 配置（保留用于兼容性）
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./news.db')
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB 配置
MONGODB_URL = os.getenv('MONGODB_URL')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME')

def get_mongo_client():
    return MongoClient(MONGODB_URL)

    
    return MongoClient(MONGODB_URL, **client_options)

def get_mongo_db():
    """获取 MongoDB 数据库实例"""
    client = get_mongo_client()
    return client[MONGODB_DB_NAME]

def get_mongo_collection(collection_name):
    """获取指定的 MongoDB 集合"""
    db = get_mongo_db()
    return db[collection_name]

# 在 startup 时创建表（SQLAlchemy）
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()