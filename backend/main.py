from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from routes.news import router as news_router
from routes.pay import router as pay_router
from app.db import SessionLocal
from app.models import Vote
from app.db import init_db

init_db()

app = FastAPI()

# CORS 配置，允许所有域名访问（可根据需要指定前端域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议写成 ["https://www.simplenews.online"]
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
    db = SessionLocal()
    try:
        votes = db.query(Vote).all()
        return {"votes": [{"title": vote.title, "count": vote.count} for vote in votes]}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)