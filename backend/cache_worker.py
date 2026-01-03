import logging
from app.news.postgres_service import PostgresService
from app.db import SessionLocal
from news.fetch_news import get_tech_news
import time
from app import redis_client
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refresh_news_cache():
    """Refresh news cache"""
    try:
        logger.info("🔄 Starting news cache refresh...")
        
        # Get new news data
        news_items = get_tech_news(force_refresh=True)
        logger.info(f"📰 Fetched {len(news_items)} news items")
        
        if not news_items:
            logger.warning("⚠️ No news data fetched")
            return
        
        # Save to database
        db = SessionLocal()
        try:
            pg_service = PostgresService(db)
            success = pg_service.save_news(news_items)
            if success:
                logger.info("✅ News cache refresh successful")
            else:
                logger.error("❌ News cache refresh failed")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error refreshing news cache: {e}")

def prewarm_homepage_cache():
    db = SessionLocal()
    pg_service = PostgresService(db)
    sort_types = ["smart", "time", "headlines"]
    for sort_by in sort_types:
        cache_key = f"news:{sort_by}:0:20:all"
        news = pg_service.get_news(offset=0, limit=20, sort_by=sort_by, source_filter=None)
        redis_client.setex(cache_key, 120, json.dumps(news, ensure_ascii=False))
    db.close()

if __name__ == "__main__":
    while True:
        print("[CacheWorker] Prewarming homepage news cache...")
        prewarm_homepage_cache()
        time.sleep(300)  # 5 minutes 