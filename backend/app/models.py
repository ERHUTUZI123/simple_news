from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
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
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 新增字段支持智能排序
    published_at = Column(DateTime, default=datetime.utcnow)  # 新闻发布时间
    summary_ai = Column(JSON)  # AI摘要结构 {"brief": "...", "detailed": "...", "structure_score": 4.5}
    headline_count = Column(Integer, default=0)  # 点赞数
    keywords = Column(JSON)  # 关键词数组 ["AI", "regulation", "Europe"]
    score = Column(Float, default=0.0)  # 综合评分

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, index=True, nullable=False)
    count = Column(Integer, default=0)

class SavedArticle(Base):
    __tablename__ = "saved_articles"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    news_id = Column(String, primary_key=True)
    saved_at = Column(TIMESTAMP, server_default=func.now()) 