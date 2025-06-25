from sqlalchemy import Column, Integer, String, Boolean
from news.db import Base

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    count = Column(Integer, default=0)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    is_subscribed = Column(Boolean, default=False)