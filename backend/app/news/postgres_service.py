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

    # 获取新闻
    def get_news(self, offset=0, limit=20, sort_by="time", source_filter=None) -> List[Dict]:
        """获取新闻，只支持时间排序"""
        try:
            use_cache = (offset == 0)
            cache_key = f"news:{sort_by}:{offset}:{limit}:{source_filter or 'all'}"
            if use_cache:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            print(f"🔍 DEBUG: Querying news with offset={offset}, limit={limit}, sort_by={sort_by}")
            
            query = self.db.query(News)
            
            # 应用来源过滤
            if source_filter:
                query = query.filter(News.source.ilike(f"%{source_filter}%"))
            
            # 只支持时间排序
            query = query.order_by(desc(News.published_at))
            
            # 应用分页
            news_items = query.offset(offset).limit(limit).all()
            
            print(f"🔍 DEBUG: Found {len(news_items)} news items in database")
            
            # 转换为字典格式
            results = []
            for item in news_items:
                try:
                    # 确保日期格式正确
                    date_str = None
                    published_at = item.published_at
                    if published_at:
                        try:
                            # 确保是UTC时间并格式化为ISO字符串
                            if published_at.tzinfo is None:
                                # 如果没有时区信息，假设是UTC
                                date_str = published_at.isoformat() + 'Z'
                            else:
                                # 如果有时区信息，转换为UTC
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

    # 保存新闻
    def save_news(self, news_items: List[Dict]) -> bool:
        """保存新闻到数据库"""
        try:
            print(f"🔍 DEBUG: Saving {len(news_items)} news items to database")
            
            if not news_items:
                print("⚠️ No news items to save")
                return True
            
            saved_count = 0
            for i, item in enumerate(news_items):
                try:
                    # 基本验证
                    if not item.get("title") or not item.get("content") or not item.get("link"):
                        print(f"⚠️ Skipping item {i}: missing required fields")
                        continue
                    
                    # 检查是否已存在（只检查标题）
                    existing = self.db.query(News).filter(News.title == item["title"]).first()
                    if existing:
                        print(f"🔍 DEBUG: Skipping existing article: {item['title'][:50]}...")
                        continue
                    
                    # 标准化日期处理
                    raw_date = item.get("date", "")
                    try:
                        if isinstance(raw_date, str):
                            # 解析RSS日期字符串并转换为UTC时间
                            from dateutil import parser as dateparser
                            from dateutil import tz
                            parsed_date = dateparser.parse(raw_date)
                            if parsed_date.tzinfo:
                                # 如果有时区信息，转换为UTC
                                utc_date = parsed_date.astimezone(tz.tzutc())
                                normalized_date = utc_date.replace(tzinfo=None)
                            else:
                                # 如果没有时区信息，假设是UTC
                                normalized_date = parsed_date
                        else:
                            normalized_date = raw_date
                    except Exception as e:
                        print(f"⚠️ Date parsing failed for item {i}: {e}")
                        from datetime import datetime
                        normalized_date = datetime.utcnow()
                    
                    # 创建新闻条目
                    news_item = News(
                        id=uuid.uuid4(),
                        title=item["title"],
                        content=item["content"],
                        link=item["link"],
                        date=normalized_date,
                        source=item.get("source", ""),
                        published_at=normalized_date,
                        created_at=datetime.utcnow(),
                        keywords=[]  # 简化，不使用关键词
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

    # 获取投票数
    def get_vote_count(self, title: str) -> int:
        """获取新闻的投票数"""
        try:
            vote = self.db.query(Vote).filter(Vote.title == title).first()
            return vote.count if vote else 0
        except Exception as e:
            print(f"Error getting vote count: {e}")
            return 0

    # 更新投票
    def update_vote(self, title: str, delta: int) -> int:
        """更新新闻的投票数"""
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

    # 获取文章详情
    def get_article_by_title(self, title: str) -> Dict:
        """根据标题获取文章详情"""
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

    # 确保关键词是数组格式
    def _ensure_keywords_array(self, keywords: Any) -> List[str]:
        """确保关键词是数组格式"""
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

    # 用户保存文章相关方法
    def save_article_for_user(self, user_id: UUID, news_id: UUID) -> bool:
        """为用户保存文章"""
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
        """从用户收藏中移除文章"""
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
        """获取用户保存的文章列表"""
        try:
            saved_articles = self.db.query(SavedArticle).filter(
                SavedArticle.user_id == user_id
            ).all()
            articles = []
            for saved in saved_articles:
                article = self.db.query(News).filter(News.id == saved.news_id).first()
                if article:
                    # 组装前端需要的字段
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
        """检查文章是否已被用户保存"""
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
        """保存用户信息到数据库"""
        try:
            # 检查用户是否已存在
            result = self.db.execute(
                text("SELECT id FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                # 用户已存在，更新信息
                self.db.execute(
                    text("""
                        UPDATE users 
                        SET email = :email, name = :name 
                        WHERE id = :user_id
                    """),
                    {"user_id": user_id, "email": email, "name": name}
                )
            else:
                # 创建新用户
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
        """标准化标题用于去重比较"""
        # 转换为小写
        normalized = title.lower()
        # 移除多余的空白字符
        normalized = re.sub(r'\s+', ' ', normalized)
        # 移除常见的标点符号
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # 移除首尾空白
        normalized = normalized.strip()
        return normalized

    def _is_duplicate_title(self, new_title: str) -> bool:
        """检查标题是否重复（简化版本）"""
        try:
            # 只检查完全相同的标题
            existing = self.db.query(News).filter(News.title == new_title).first()
            return existing is not None
        except Exception as e:
            print(f"Error checking duplicate title: {e}")
            return False 