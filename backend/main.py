from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.news import router as news_router
from routes.pay import router as pay_router
from news.db import init_db
from models import Vote
init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router)
app.include_router(pay_router)

@app.get("/")
def root():
    return {"message": "TechPulse backend is running"}

@app.get("/votes/")
def get_votes():
    votes = db.query(Vote).filter(Vote.title).all()
    return {"votes": votes}