# Column: column in a db table, each one defined with data type and constriants
# Integer, String, DateTime, Float, JSON TIMESTAP, ForeignKey (Represents a foreign key constraint, linking one table to another)
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, TIMESTAMP, ForeignKey, UUID
# UUID is unique identifiers
# Provide access for SQL functions such as now() for getting the current timestamp
from sqlalchemy.sql import func
# Datetime is a py lib for working with times and dates
from datetime import datetime
# Import Base
from db import Base

# Define user model, which maps to the users table in db
class Users(Base):
    __tablename__ = "users"
    # id rep the primary key since primary_key=True
    # Column just builds a column within db
    # UUID(as_uuid=True) specifies that the column stores UUIDs as 16-byte binary to increase efficiency 
    # primary_key=True defines id as the primary key
    id = Column(UUID(as_uuid=True), primary_key=True)
    # email rep user's email
    # String means a string
    # unique=True to make it unique
    # index=True to creates an index on thi scolumn to speed up queries since email requires checkup and is not
    #   set to be the primary key
    # nullable=False to ensures this column cannot be empty
    email = Column(String, unique=True, index=True, nullable=False)
    # rep name of user
    # String means a string
    name = Column(String, nullable=False)
    # created_at stores the timestamp when the user was created
    # automatically sets the current utc time when a new record is created
    create_at = Column(DateTime, default=datetime.utcnow)

# Define News, which maps to the news table in the db
class News(Base):
    # __tablename__ = 'news'
    __tablename__ = "news"
    # news id
    id = Column(UUID(as_uuid=True), primary_key=True)
    # title is string and u wanna index them and make sure they are not empty
    title = Column(String, unique=True, index=True, nullable=False)
    # content string and doesnt need to be indexed but still non-empty
    content = Column(String, nullable=False)
    # summary is just string
    summary = Column(String)
    # link is just string
    link = Column(String)
    # soruce is string
    source = Column(String)
    # created_at is datetime and default=datetime.utcnow
    create_at = Column(DateTime, default=datetime.utcnow)
    # followings are designed for supporting smart sort
    # published_at is datetime and default=datetime.utcnow
    publish_at = Column(DateTime, default=datetime.utcnow)
    # summary JSON
    # AI summary structure
    #    {"brief": "...", "detailed": "...", "structure_score": 4.5}
    summary = Column(JSON) 
    # likes is integer and default=0 
    likes = Column(Integer, default=0) # likes
    # keywords is in JSON format
    keywords = Column(JSON)  # keywords ["AI", "regulation", "Europe"]
    
class Saves(Base):
    __tablename__ = "saves"  
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    news_id = Column(UUID(as_uuid=True), ForeignKey("news.id"))
    save_at = Column(TIMESTAMP, default=datetime.utcnow)
    rating = Column(Float, default=0.0) 