"""
main.py

This file starts the original OneMinNews backend API. For the scalable news summarization and rating AI agent API, use:
    uvicorn backend.app.api:app --reload
or see backend/start_api.sh
"""
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

# CORS configuration, allow all domains to access (can specify frontend domain as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, recommend writing as ["https://www.simplenews.online"]
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
    try:
        # Actually execute news fetching and cache refresh
        refresh_news_cache()
        logging.info('scheduled rss fetching completed successfully')
    except Exception as e:
        logging.error(f'scheduled rss fetching failed: {e}')

# Run it every 10 minutes
scheduler.add_job(fetch_and_cache_news, 
                  'interval',
                  minutes=5)
scheduler.start()

# Background scheduled task
def background_news_refresh():
    """Background news refresh task"""
    while True:
        try:
            print("🔄 Background task: Starting news refresh...")
            refresh_news_cache()
            print("✅ Background task: News refresh completed")
        except Exception as e:
            print(f"❌ Background task: News refresh failed - {e}")
        
        # Wait 15 minutes
        time.sleep(15 * 60)

# Start background task
@app.on_event("startup")
async def startup_event():
    """Start background task when application starts"""
    print("🚀 Starting background news refresh task...")
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