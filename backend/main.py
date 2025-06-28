from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import threading
import time
from routes.news import router as news_router
from routes.pay import router as pay_router
from app.db import SessionLocal
from app.models import Vote
from app.db import init_db
from cache_worker import refresh_news_cache
from apscheduler.schedulers.background import BackgroundScheduler
from news.fetch_news import fetch_from_rss
import logging

init_db()

app = FastAPI()

scheduler = BackgroundScheduler()
logging.basicConfig(level=logging.INFO)

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


cached_news = []

def fetch_and_cache_news():
    global cached_news
    logging.info('scheduled rss fetching...')

# Run it every 10 minutes
scheduler.add_job(fetch_and_cache_news, 
                  'interval',
                  minutes=5)
scheduler.start()

# 后台定时任务
def background_news_refresh():
    """后台新闻刷新任务"""
    while True:
        try:
            print("🔄 后台任务：开始刷新新闻...")
            refresh_news_cache()
            print("✅ 后台任务：新闻刷新完成")
        except Exception as e:
            print(f"❌ Background task: News refresh failed - {e}")
        
        # 等待15分钟
        time.sleep(15 * 60)

# 启动后台任务
@app.on_event("startup")
async def startup_event():
    """应用启动时启动后台任务"""
    print("🚀 启动后台新闻刷新任务...")
    thread = threading.Thread(target=background_news_refresh, daemon=True)
    thread.start()

@app.get("/")
def root():
    return {"message": "OneMinNews backend is running"}

@app.get("/votes/")
def get_votes():
    db = SessionLocal()
    try:
        votes = db.query(Vote).all()
        return {"votes": [{"title": vote.title, "count": vote.count} for vote in votes]}
    finally:
        db.close()

@app.get("/news/auto")
def get_auto_news():
    return cached_news

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)