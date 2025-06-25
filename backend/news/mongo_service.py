from news.db import get_mongo_collection
from models import NewsDocument, VoteDocument, UserDocument
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MongoService:
    """MongoDB 服务类"""
    
    def __init__(self):
        self.news_collection = get_mongo_collection("news")
        self.votes_collection = get_mongo_collection("votes")
        self.users_collection = get_mongo_collection("users")
    
    def save_news(self, news_items: List[Dict]) -> bool:
        """保存新闻到 MongoDB"""
        try:
            # 清空现有新闻
            self.news_collection.delete_many({})
            logger.info("🧹 Cleared existing news collection")

            if news_items:
                documents = []
                for item in news_items:
                    news_doc = NewsDocument(
                        title=item["title"],
                        content=item["content"],
                        summary=item.get("summary") or "",
                        link=item["link"],
                        date=item["date"],
                        source=item["source"]
                    )
                    doc = news_doc.to_dict()

                    # 添加默认评分字段
                    doc["ai_score"] = 5
                    doc["vote_count"] = 0
                    doc["comprehensive_score"] = 0.5
                    doc["created_at"] = datetime.utcnow()

                    documents.append(doc)
                
                self.news_collection.insert_many(documents)
                logger.info(f"✅ Saved {len(documents)} news items to MongoDB")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving news to MongoDB: {e}")
            return False
    
    def get_news(self, offset: int = 0, limit: int = 20, sort_by: str = "smart", source_filter: Optional[str] = None) -> List[Dict]:
        """从 MongoDB 获取新闻"""
        try:
            query = {}
            if source_filter:
                query["source"] = {"$regex": source_filter, "$options": "i"}
            
            # 安全排序逻辑
            if sort_by == "smart":
                sort = [("comprehensive_score", -1), ("date", -1)]  # fallback
            elif sort_by == "time":
                sort = [("date", -1)]
            elif sort_by == "popular":
                sort = [("vote_count", -1)]
            elif sort_by == "ai_quality":
                sort = [("ai_score", -1)]
            else:
                sort = [("created_at", -1)]
            
            cursor = self.news_collection.find(query).sort(sort).skip(offset).limit(limit)
            news_items = list(cursor)
            
            for item in news_items:
                item.pop("_id", None)

            logger.info(f"📥 Retrieved {len(news_items)} news items from MongoDB")
            return news_items
            
        except Exception as e:
            logger.error(f"❌ Error retrieving news from MongoDB: {e}")
            return []

    def get_vote_count(self, title: str) -> int:
        try:
            vote_doc = self.votes_collection.find_one({"title": title})
            return vote_doc["count"] if vote_doc else 0
        except Exception as e:
            logger.error(f"❌ Error getting vote count for {title}: {e}")
            return 0
    
    def update_vote(self, title: str, delta: int) -> int:
        try:
            self.votes_collection.update_one(
                {"title": title},
                {"$inc": {"count": delta}, "$set": {"updated_at": datetime.utcnow()}},
                upsert=True
            )
            vote_doc = self.votes_collection.find_one({"title": title})
            new_count = vote_doc["count"] if vote_doc else 0
            logger.info(f"👍 Updated vote for {title}: {delta}, new count: {new_count}")
            return new_count
        except Exception as e:
            logger.error(f"❌ Error updating vote for {title}: {e}")
            return 0

    def get_user(self, email: str) -> Optional[Dict]:
        try:
            user_doc = self.users_collection.find_one({"email": email})
            if user_doc:
                user_doc.pop("_id", None)
            return user_doc
        except Exception as e:
            logger.error(f"❌ Error getting user {email}: {e}")
            return None
    
    def create_user(self, email: str, is_subscribed: bool = False) -> bool:
        try:
            user_doc = UserDocument(email=email, is_subscribed=is_subscribed)
            self.users_collection.insert_one(user_doc.to_dict())
            logger.info(f"👤 Created user: {email}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating user {email}: {e}")
            return False
    
    def update_user_subscription(self, email: str, is_subscribed: bool) -> bool:
        try:
            result = self.users_collection.update_one(
                {"email": email},
                {"$set": {"is_subscribed": is_subscribed}}
            )
            logger.info(f"🔔 Updated subscription for {email}: {is_subscribed}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"❌ Error updating subscription for {email}: {e}")
            return False

    def get_cached_news(self, hours: int = 24) -> List[Dict]:
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            cursor = self.news_collection.find({
                "created_at": {"$gte": cutoff_time}
            }).sort("created_at", -1)
            
            news_items = list(cursor)
            for item in news_items:
                item.pop("_id", None)
            
            logger.info(f"📦 Retrieved {len(news_items)} cached news items")
            return news_items
        except Exception as e:
            logger.error(f"❌ Error retrieving cached news: {e}")
            return []
