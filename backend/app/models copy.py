from sqlalchemy import Column, String, DateTime, Integer, Float, JSON, TIMESTAMP, ForeignKey
from sqlalchemy import UUID
from sqlalchemy.sql import func
from datetime import datetime
from db import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    create_at = Column(DateTime, default=datetime.utcnow)

class News(Base):
    __tablename__ = "news"
    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String, unique=True, index=True, nullable=False)
    content = Column(String, nullable=False)
    link = Column(String)
    source = Column(String)
    summary = Column(JSON)
    keywords = Column(JSON)
    create_at = Column(DateTime, default=datetime.utcnow)
    publish_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)

class Saves(Base):
    __tablename__ = "saves"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    news_id = Column(UUID(as_uuid=True), ForeignKey("news.id"))
    save_at = Column(TIMESTAMP, default=datetime.utcnow)