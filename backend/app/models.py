from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, index=True, nullable=False)
    content = Column(String, nullable=False)
    summary = Column(String)
    link = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
    ai_score = Column(Float, default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, index=True, nullable=False)
    count = Column(Integer, default=0) 