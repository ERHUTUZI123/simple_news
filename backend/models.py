from sqlalchemy import Column, Integer, String
from news.db import Base

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    count = Column(Integer, default=0)