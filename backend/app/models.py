from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class News(Base):
    __tablename__ = "news"
    id = Column(UUID(as_uuid=True), primary_key=True)
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
    smart_score = Column(Float, default=0.0)  # 智能评分 (Smart Sort V2)

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, index=True, nullable=False)
    count = Column(Integer, default=0)

class SavedArticle(Base):
    __tablename__ = "saves"  # 匹配数据库表名
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    news_id = Column(UUID(as_uuid=True), ForeignKey("news.id"))
    created_at = Column(TIMESTAMP, server_default=func.now()) 