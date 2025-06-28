from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models import News, Vote, SavedArticle, User
from app.scoring import calculate_news_score, extract_keywords_from_text, build_existing_keyword_map
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
from app.smart_scoring import compute_smart_score, get_score_breakdown

class PostgresService:
    def __init__(self, db: Session):
        self.db = db

    # 获取新闻
    def get_news(self, offset=0, limit=20, sort_by="smart", source_filter=None) -> List[Dict]:
        """获取新闻，支持智能排序，仅缓存首页数据（offset=0）"""
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
            
            # 应用排序
            if sort_by == "smart_score":
                # 智能评分排序：按smart_score降序
                query = query.order_by(desc(News.smart_score))
            elif sort_by == "smart":
                # 智能排序：按综合评分降序
                query = query.order_by(desc(News.score))
            elif sort_by == "time":
                # 时间排序：按发布时间降序
                query = query.order_by(desc(News.published_at))
            elif sort_by == "headlines":
                # 点赞数排序：按点赞数降序
                query = query.order_by(desc(News.headline_count))
            else:
                # 默认使用智能评分排序
                query = query.order_by(desc(News.smart_score))
            
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
                        "score": float(item.score) if item.score is not None else 0.0,  # Ensure float
                        "smart_score": float(item.smart_score) if item.smart_score is not None else 0.0,  # 智能评分
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
        """保存新闻到数据库，包含智能评分"""
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
                    
                    # 提取关键词
                    try:
                        keywords = extract_keywords_from_text(item["title"] + " " + item["content"])
                    except Exception as e:
                        print(f"⚠️ Keyword extraction failed for item {i}: {e}")
                        keywords = []
                    
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
                    
                    # 创建AI摘要结构
                    summary_ai = {
                        "brief": "",
                        "detailed": "",
                        "structure_score": 3.0  # 默认评分
                    }
                    
                    # 计算综合评分
                    try:
                        score = calculate_news_score(
                            published_at=normalized_date,
                            summary_ai=summary_ai,
                            source=item.get("source", ""),
                            keywords=keywords,
                            headline_count=0,  # 新新闻初始点赞数为0
                            existing_keyword_map={}  # 简化，不使用现有关键词映射
                        )
                    except Exception as e:
                        print(f"⚠️ Score calculation failed for item {i}: {e}")
                        score = 1.0  # 默认评分
                    
                    # 计算智能评分
                    try:
                        # 获取现有新闻用于新颖性计算
                        existing_news = self.get_news(0, 1000, "time")
                        existing_titles = [news.get('title', '') for news in existing_news]
                        
                        # 准备文章数据用于评分
                        article_data = {
                            'title': item["title"],
                            'content': item["content"],
                            'source': item.get("source", ""),
                            'published_at': normalized_date,
                            'headline_count': 0,
                            'summary_ai': summary_ai
                        }
                        
                        # 计算智能评分
                        smart_score = compute_smart_score(article_data, existing_news)
                        
                        # 可选：获取详细评分分解（用于调试）
                        score_breakdown = get_score_breakdown(article_data, existing_news)
                        print(f"🔍 DEBUG: Smart score breakdown for '{item['title'][:50]}...': {score_breakdown}")
                        
                    except Exception as e:
                        print(f"⚠️ Error computing smart score: {e}")
                        smart_score = 0.0
                    
                    # 创建新闻对象
                    news = News(
                        id=str(uuid.uuid4()),
                        title=item["title"],
                        content=item["content"],
                        summary=item.get("summary", ""),
                        link=item["link"],
                        date=normalized_date,
                        source=item.get("source", ""),
                        published_at=normalized_date,
                        summary_ai=summary_ai,
                        headline_count=0,
                        keywords=keywords,
                        score=score,
                        smart_score=smart_score  # 添加智能评分
                    )
                    
                    self.db.add(news)
                    self.db.commit()
                    saved_count += 1
                except Exception as e:
                    self.db.rollback()
                    print(f"❌ Error saving individual article {i}: {e}")
                    continue
            
            # 最终提交
            self.db.commit()
            print(f"🔍 DEBUG: Successfully saved {saved_count} new articles to database")
            return True
        except Exception as e:
            print(f"❌ Error saving news: {e}")
            import traceback
            traceback.print_exc()
            self.db.rollback()
            return False

    # 获取投票数
    def get_vote_count(self, title: str) -> int:
        """获取投票数"""
        try:
            vote = self.db.query(Vote).filter(Vote.title == title).first()
            return int(getattr(vote, "count", 0)) if vote else 0
        except Exception as e:
            print(f"Error getting vote count: {e}")
            return 0

    # 更新投票
    def update_vote(self, title: str, delta: int) -> int:
        """更新投票数"""
        try:
            vote = self.db.query(Vote).filter(Vote.title == title).first()
            if not vote:
                vote = Vote(title=title, count=delta)
                self.db.add(vote)
            else:
                current_count = int(getattr(vote, "count", 0))
                new_count = max(0, current_count + delta)
                setattr(vote, "count", new_count)
            
            # 同时更新新闻的headline_count
            news = self.db.query(News).filter(News.title == title).first()
            if news:
                news.headline_count = int(getattr(vote, "count", 0))
                # 重新计算评分
                self._recalculate_news_score(news)
            
            self.db.commit()
            return int(getattr(vote, "count", 0))
        except Exception as e:
            print(f"Error updating vote: {e}")
            self.db.rollback()
            return 0

    def _recalculate_news_score(self, news: News):
        """重新计算新闻评分"""
        try:
            # 获取现有新闻的关键词映射
            existing_news = self.get_news(0, 1000, "time")
            existing_keyword_map = build_existing_keyword_map(existing_news)
            
            # 重新计算评分
            published_at = news.published_at or datetime.utcnow()
            summary_ai = news.summary_ai or {}
            keywords = news.keywords or []
            headline_count = news.headline_count or 0
            
            score = calculate_news_score(
                published_at=published_at,
                summary_ai=summary_ai,
                source=news.source,
                keywords=keywords,
                headline_count=headline_count,
                existing_keyword_map=existing_keyword_map
            )
            
            news.score = score
        except Exception as e:
            print(f"Error recalculating score: {e}")

    def update_ai_summary(self, title: str, brief_summary: str, detailed_summary: str, structure_score: float = 3.0):
        """更新AI摘要和结构评分"""
        try:
            news = self.db.query(News).filter(News.title == title).first()
            if news:
                news.summary_ai = {
                    "brief": brief_summary,
                    "detailed": detailed_summary,
                    "structure_score": structure_score
                }
                # 重新计算评分
                self._recalculate_news_score(news)
                self.db.commit()
        except Exception as e:
            print(f"Error updating AI summary: {e}")
            self.db.rollback()

    def get_article_by_title(self, title: str) -> Dict:
        """根据标题获取文章，带缓存"""
        try:
            # 构造缓存key
            cache_key = f"article:{title}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 直接查询数据库
            news = self.db.query(News).filter(News.title == title).first()
            
            if news:
                # 确保日期格式正确
                date_str = None
                published_at = news.published_at
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
                
                result = {
                    "id": str(news.id),  # Convert UUID to string
                    "title": news.title,
                    "content": news.content,  # Frontend expects 'content'
                    "link": news.link,
                    "date": date_str,  # Frontend expects 'date'
                    "source": news.source,
                    "vote_count": self.get_vote_count(news.title),
                    "score": float(news.score) if news.score is not None else 0.0,
                    "keywords": self._ensure_keywords_array(news.keywords)
                }
                
                # 设置缓存，600秒
                redis_client.setex(cache_key, 600, json.dumps(result, ensure_ascii=False))
                return result
            
            # 没找到文章
            result = {"error": "Article not found"}
            redis_client.setex(cache_key, 600, json.dumps(result, ensure_ascii=False))
            return result
        except Exception as e:
            print(f"Error getting article by title: {e}")
            return {"error": "Article not found"}

    def _ensure_keywords_array(self, keywords: Any) -> List[str]:
        """确保关键词是数组，处理各种可能的格式"""
        try:
            if keywords is None:
                return []
            elif isinstance(keywords, str):
                # 如果是字符串，尝试解析为JSON
                try:
                    import json
                    # 处理可能的转义字符
                    cleaned_keywords = keywords.strip()
                    if cleaned_keywords.startswith('"') and cleaned_keywords.endswith('"'):
                        # 如果是双引号包围的字符串，先去掉引号
                        cleaned_keywords = cleaned_keywords[1:-1]
                    
                    parsed = json.loads(cleaned_keywords)
                    if isinstance(parsed, list):
                        return [str(kw) for kw in parsed if kw is not None]
                    else:
                        return [cleaned_keywords]  # 如果解析失败，返回原字符串作为单个元素
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Failed to parse keywords JSON: {e}, keywords: {keywords}")
                    return [keywords]  # 如果解析失败，返回原字符串作为单个元素
            elif isinstance(keywords, list):
                # 确保列表中的元素都是字符串
                return [str(kw) for kw in keywords if kw is not None]
            else:
                # 其他类型，转换为字符串
                return [str(keywords)]
        except Exception as e:
            print(f"Error processing keywords: {e}, keywords: {keywords}")
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