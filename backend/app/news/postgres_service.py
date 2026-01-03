from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models import News, Vote, SavedArticle, User
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict, Any
from dateutil import parser as dateparser
from dateutil import tz
from app import redis_client
import json
from uuid import UUID
from sqlalchemy.sql import text
import re
import uuid

class PostgresService:
    def __init__(self, db: Session):
        self.db = db

    # Get news
    def get_news(self, offset=0, limit=20, sort_by="time", source_filter=None) -> List[Dict]:
        """Get news, only supports time sorting"""
        try:
            use_cache = (offset == 0)
            cache_key = f"news:{sort_by}:{offset}:{limit}:{source_filter or 'all'}"
            if use_cache:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            print(f"🔍 DEBUG: Querying news with offset={offset}, limit={limit}, sort_by={sort_by}")
            
            query = self.db.query(News)
            
            # Apply source filter
            if source_filter:
                query = query.filter(News.source.ilike(f"%{source_filter}%"))
            
            # Only support time sorting
            query = query.order_by(desc(News.published_at))
            
            # Apply pagination
            news_items = query.offset(offset).limit(limit).all()
            
            print(f"🔍 DEBUG: Found {len(news_items)} news items in database")
            
            # Convert to dictionary format
            results = []
            for item in news_items:
                try:
                    # Ensure date format is correct
                    date_str = None
                    published_at = item.published_at
                    if published_at:
                        try:
                            # Ensure UTC time and format as ISO string
                            if published_at.tzinfo is None:
                                # If no timezone info, assume UTC
                                date_str = published_at.isoformat() + 'Z'
                            else:
                                # If timezone info exists, convert to UTC
                                from datetime import timezone
                                utc_date = published_at.astimezone(timezone.utc)
                                date_str = utc_date.isoformat()
                        except Exception as e:
                            print(f"Error formatting date: {e}")
                            date_str = datetime.utcnow().isoformat() + 'Z'
                    else:
                        date_str = datetime.utcnow().isoformat() + 'Z'
                    
                    result_item = {
                        "id": str(item.id),  # Convert UUID to string
                        "title": item.title,
                        "content": item.content,
                        "link": item.link,
                        "date": date_str,
                        "source": item.source,
                        "vote_count": self.get_vote_count(item.title),
                        "keywords": self._ensure_keywords_array(item.keywords)
                    }
                    results.append(result_item)
                    print(f"🔍 DEBUG: Added item: {item.title[:50]}...")
                except Exception as e:
                    print(f"❌ Error processing news item: {e}")
                    continue
            
            print(f"🔍 DEBUG: Returning {len(results)} processed items")
            
            if use_cache:
                try:
                    redis_client.setex(cache_key, 600, json.dumps(results, ensure_ascii=False))
                except Exception as e:
                    print(f"⚠️ Cache save failed: {e}")
            
            return results
        except Exception as e:
            print(f"❌ Error getting news: {e}")
            import traceback
            traceback.print_exc()
            return []

    # Save news
    def save_news(self, news_items: List[Dict]) -> bool:
        """Save news to database"""
        try:
            print(f"🔍 DEBUG: Saving {len(news_items)} news items to database")
            
            if not news_items:
                print("⚠️ No news items to save")
                return True
            
            saved_count = 0
            for i, item in enumerate(news_items):
                try:
                    # Basic validation
                    if not item.get("title") or not item.get("content") or not item.get("link"):
                        print(f"⚠️ Skipping item {i}: missing required fields")
                        continue
                    
                    # Check if already exists (only check title)
                    existing = self.db.query(News).filter(News.title == item["title"]).first()
                    if existing:
                        print(f"🔍 DEBUG: Skipping existing article: {item['title'][:50]}...")
                        continue
                    
                    # Normalize date handling
                    raw_date = item.get("date", "")
                    try:
                        if isinstance(raw_date, str):
                            # Parse RSS date string and convert to UTC time
                            from dateutil import parser as dateparser
                            from dateutil import tz
                            parsed_date = dateparser.parse(raw_date)
                            if parsed_date.tzinfo:
                                # If timezone info exists, convert to UTC
                                utc_date = parsed_date.astimezone(tz.tzutc())
                                normalized_date = utc_date.replace(tzinfo=None)
                            else:
                                # If no timezone info, assume UTC
                                normalized_date = parsed_date
                        else:
                            normalized_date = raw_date
                    except Exception as e:
                        print(f"⚠️ Date parsing failed for item {i}: {e}")
                        from datetime import datetime
                        normalized_date = datetime.utcnow()
                    
                    # Create news item
                    news_item = News(
                        id=uuid.uuid4(),
                        title=item["title"],
                        content=item["content"],
                        link=item["link"],
                        date=normalized_date,
                        source=item.get("source", ""),
                        published_at=normalized_date,
                        created_at=datetime.utcnow(),
                        keywords=[]  # Simplified, not using keywords
                    )
                    
                    self.db.add(news_item)
                    saved_count += 1
                    print(f"✅ Saved: {item['title'][:50]}...")
                    
                except Exception as e:
                    print(f"❌ Error saving item {i}: {e}")
                    continue
            
            self.db.commit()
            print(f"✅ Successfully saved {saved_count} news items")
            return True
            
        except Exception as e:
            print(f"❌ Error saving news: {e}")
            self.db.rollback()
            return False

    # Get vote count
    def get_vote_count(self, title: str) -> int:
        """Get news vote count"""
        try:
            vote = self.db.query(Vote).filter(Vote.title == title).first()
            return vote.count if vote else 0
        except Exception as e:
            print(f"Error getting vote count: {e}")
            return 0

    # Update vote
    def update_vote(self, title: str, delta: int) -> int:
        """Update news vote count"""
        try:
            vote = self.db.query(Vote).filter(Vote.title == title).first()
            if vote:
                vote.count += delta
            else:
                vote = Vote(title=title, count=delta)
                self.db.add(vote)
            
            self.db.commit()
            return vote.count
        except Exception as e:
            print(f"Error updating vote: {e}")
            self.db.rollback()
            return 0

    # Get article details
    def get_article_by_title(self, title: str) -> Dict:
        """Get article details by title"""
        try:
            news = self.db.query(News).filter(News.title == title).first()
            if not news:
                return {"error": "Article not found"}
            
            return {
                "id": str(news.id),
                "title": news.title,
                "content": news.content,
                "link": news.link,
                "date": news.date.isoformat() if news.date else None,
                "source": news.source,
                "vote_count": self.get_vote_count(news.title)
            }
        except Exception as e:
            print(f"Error getting article: {e}")
            return {"error": "Failed to get article"}

    # Ensure keywords are in array format
    def _ensure_keywords_array(self, keywords: Any) -> List[str]:
        """Ensure keywords are in array format"""
        try:
            if not keywords:
                return []
            
            if isinstance(keywords, str):
                try:
                    parsed = json.loads(keywords)
                    if isinstance(parsed, list):
                        return parsed
                    else:
                        return []
                except json.JSONDecodeError:
                    return []
            
            if isinstance(keywords, list):
                return keywords
            
            return []
        except Exception as e:
            print(f"Error ensuring keywords array: {e}")
            return []

    # User saved article related methods
    def save_article_for_user(self, user_id: UUID, news_id: UUID) -> bool:
        """Save article for user"""
        try:
            existing = self.db.query(SavedArticle).filter(
                SavedArticle.user_id == user_id,
                SavedArticle.news_id == news_id
            ).first()
            if existing:
                return True
            saved_article = SavedArticle(user_id=user_id, news_id=news_id)
            self.db.add(saved_article)
            self.db.commit()
            print(f"✅ Saved article {news_id} for user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error saving article for user: {e}")
            self.db.rollback()
            return False

    def remove_article_from_user(self, user_id: UUID, news_id: UUID) -> bool:
        """Remove article from user's saved articles"""
        try:
            saved_article = self.db.query(SavedArticle).filter(
                SavedArticle.user_id == user_id,
                SavedArticle.news_id == news_id
            ).first()
            if saved_article:
                self.db.delete(saved_article)
                self.db.commit()
                print(f"✅ Removed article {news_id} from user {user_id}")
                return True
            else:
                return True
        except Exception as e:
            print(f"❌ Error removing article from user: {e}")
            self.db.rollback()
            return False

    def get_saved_articles_for_user(self, user_id: UUID) -> list:
        """Get user's saved articles list"""
        try:
            saved_articles = self.db.query(SavedArticle).filter(
                SavedArticle.user_id == user_id
            ).all()
            articles = []
            for saved in saved_articles:
                article = self.db.query(News).filter(News.id == saved.news_id).first()
                if article:
                    # Assemble fields needed by frontend
                    articles.append({
                        "id": str(article.id),
                        "title": article.title,
                        "content": article.content,
                        "summary": article.summary,
                        "link": article.link,
                        "date": article.date.isoformat() if article.date else None,
                        "source": article.source,
                        "created_at": article.created_at.isoformat() if article.created_at else None,
                        "published_at": article.published_at.isoformat() if article.published_at else None,
                        "summary_ai": article.summary_ai,
                        "headline_count": article.headline_count,
                        "keywords": article.keywords,
                        "score": article.score
                    })
            print(f"✅ Retrieved {len(articles)} saved articles for user {user_id}")
            return articles
        except Exception as e:
            print(f"❌ Error getting saved articles for user: {e}")
            return []

    def is_article_saved_by_user(self, user_id: UUID, news_id: UUID) -> bool:
        """Check if article is saved by user"""
        try:
            saved_article = self.db.query(SavedArticle).filter(
                SavedArticle.user_id == user_id,
                SavedArticle.news_id == news_id
            ).first()
            return saved_article is not None
        except Exception as e:
            print(f"❌ Error checking if article is saved by user: {e}")
            return False

    def save_user(self, user_id: str, email: str, name: str) -> bool:
        """Save user information to database"""
        try:
            # Check if user already exists
            result = self.db.execute(
                text("SELECT id FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                # User exists, update information
                self.db.execute(
                    text("""
                        UPDATE users 
                        SET email = :email, name = :name 
                        WHERE id = :user_id
                    """),
                    {"user_id": user_id, "email": email, "name": name}
                )
            else:
                # Create new user
                self.db.execute(
                    text("""
                        INSERT INTO users (id, email, name, created_at) 
                        VALUES (:user_id, :email, :name, NOW())
                    """),
                    {"user_id": user_id, "email": email, "name": name}
                )
            
            self.db.commit()
            print(f"✅ Saved user {user_id} to database")
            return True
            
        except Exception as e:
            print(f"❌ Error saving user: {e}")
            self.db.rollback()
            return False

    def _normalize_title(self, title: str) -> str:
        """Normalize title for duplicate comparison"""
        # Convert to lowercase
        normalized = title.lower()
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        # Remove common punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Remove leading/trailing whitespace
        normalized = normalized.strip()
        return normalized

    def _is_duplicate_title(self, new_title: str) -> bool:
        """Check if title is duplicate (simplified version)"""
        try:
            # Only check for exactly the same title
            existing = self.db.query(News).filter(News.title == new_title).first()
            return existing is not None
        except Exception as e:
            print(f"Error checking duplicate title: {e}")
            return False 