# from a ORM import a database-creating engine
# it will create a connection pool between our application and the database
from sqlalchemy import create_engine
# declarative_base is a fucntion used for creating Base,
# SQLALchemy will map Base class to a database table
# u can specify the table name and columns using class attributes
from sqlalchemy.ext.declarative import declarative_base
# create a session 
# session is used to interact with database(e.g., querying, inserting, updating data)
from sqlalchemy.orm import sessionmaker
# os is a py module used for interacting with operating system
import os

# postgreSQL configuration

# define a string specifies how to connext to the db
# os.getenv can fetch DATABASE_URL from .env local file to ensure security and flexibility
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:<your_password>@postgres.railway.internal:5432/railway')
# defines engine that manages connection pool and  translates py orm ops to sql queries
#   based on db URL created before 
# ne will be used to bind the session factory and create tables
engine = create_engine(DATABASE_URL)
# define SessionLocal whihc is a session fatory bound to the db engine
#   every time u call SessionLocal, a new session obj will be created
# autocommit=False force you to commit explicitly
# autoflush=False disables auto flushing of changes to db which give you more control 
# bind=engine binds the sessionmaker to engine created before
# autoflush i slike git.add, autocommit is like git.commit, edit->flush->commit
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Define base class for all ORM models
Base = declarative_base()

# init_db is a function used to initialize the database
def init_db():
    """初始化数据库，创建所有表"""
    # Scan all models from Base and create tables
    Base.metadata.create_all(bind=engine)

# get_db() is a generator function that provides a database session
def get_db():
    """获取数据库会话"""
    # Session() creates a new session
    db = Session()
    try:
        # yield returns the session to the caller
        # like borrow db to the caller like enpoints
        yield db
    finally:
        # db.close() ensures session is closed after using
        #   AKA releasing the db connection back to the pool 
        # one session is one connection within the connection pool
        # if too many sessions occupy the pool and make it full
        # u cannot put more sessions into it
        # so u have to close session
        db.close() 

__all__ = ["Base", "init_db", "get_db"]