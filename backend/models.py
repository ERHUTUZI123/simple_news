import os
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# 从环境变量读取 MongoDB 连接字符串，兼容 Render 部署
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://cedric:gh336699@cluster0.onzmatc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# MongoDB 连接配置，添加 SSL 选项以解决连接问题
client_options = {
    'serverSelectionTimeoutMS': 30000,
    'connectTimeoutMS': 30000,
    'socketTimeoutMS': 30000,
    'maxPoolSize': 10,
    'minPoolSize': 1,
    'maxIdleTimeMS': 30000,
    'retryWrites': True,
    'retryReads': True,
    'tls': True,
    'tlsAllowInvalidCertificates': True,  # 允许无效证书
    'tlsAllowInvalidHostnames': True,     # 允许无效主机名
}

client = MongoClient(MONGO_URI, **client_options)
db = client['oneminews']

# ------------------ MongoDB 新闻操作 ------------------

def insert_news(news: dict) -> bool:
    """插入一条新闻，news为字典。返回True成功，False失败。"""
    try:
        db.news.insert_one(news)
        return True
    except PyMongoError as e:
        print(f"MongoDB insert_news error: {e}")
        return False

def get_news(filter_dict=None, limit=20) -> list:
    """查询新闻，支持条件过滤。返回新闻列表。"""
    try:
        if filter_dict is None:
            filter_dict = {}
        return list(db.news.find(filter_dict).limit(limit))
    except PyMongoError as e:
        print(f"MongoDB get_news error: {e}")
        return []

def update_news(filter_dict, update_dict) -> int:
    """更新新闻，filter_dict为筛选条件，update_dict为更新内容。返回修改条数。"""
    try:
        result = db.news.update_many(filter_dict, {'$set': update_dict})
        return result.modified_count
    except PyMongoError as e:
        print(f"MongoDB update_news error: {e}")
        return 0

def delete_news(filter_dict) -> int:
    """删除新闻，filter_dict为筛选条件。返回删除条数。"""
    try:
        result = db.news.delete_many(filter_dict)
        return result.deleted_count
    except PyMongoError as e:
        print(f"MongoDB delete_news error: {e}")
        return 0

# ------------------ SQLAlchemy 旧表结构 ------------------

Base = declarative_base()

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    count = Column(Integer, default=0)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    is_subscribed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# MongoDB 文档模型
class NewsDocument:
    """新闻文档模型"""
    def __init__(
        self,
        title: str,
        content: str,
        summary: str,
        link: str,
        date: str,
        source: str,
        vote_count: int = 0,
        ai_score: Optional[float] = None,
        comprehensive_score: Optional[float] = None,
        created_at: Optional[datetime] = None
    ):
        self.title = title
        self.content = content
        self.summary = summary
        self.link = link
        self.date = date
        self.source = source
        self.vote_count = vote_count
        self.ai_score = ai_score
        self.comprehensive_score = comprehensive_score
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "link": self.link,
            "date": self.date,
            "source": self.source,
            "vote_count": self.vote_count,
            "ai_score": self.ai_score,
            "comprehensive_score": self.comprehensive_score,
            "created_at": self.created_at
        }

class VoteDocument:
    """投票文档模型"""
    def __init__(self, title: str, count: int = 0, updated_at: Optional[datetime] = None):
        self.title = title
        self.count = count
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "count": self.count,
            "updated_at": self.updated_at
        }

class UserDocument:
    """用户文档模型"""
    def __init__(
        self,
        email: str,
        is_subscribed: bool = False,
        created_at: Optional[datetime] = None
    ):
        self.email = email
        self.is_subscribed = is_subscribed
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "email": self.email,
            "is_subscribed": self.is_subscribed,
            "created_at": self.created_at
        }