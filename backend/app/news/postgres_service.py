from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models import News, Vote
from app.scoring import calculate_news_score, extract_keywords_from_text, build_existing_keyword_map
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict, Any
from dateutil import parser as dateparser
from dateutil import tz
from app import redis_client
import json

class PostgresService:
    def __init__(self, db: Session):
        self.db = db

    # 获取新闻
    def get_news(self, offset=0, limit=20, sort_by="smart", source_filter=None) -> List[Dict]:
        """获取新闻，支持智能排序，带缓存"""
        try:
            # 构造缓存key
            cache_key = f"news:{sort_by}:{offset}:{limit}:{source_filter or 'all'}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            query = self.db.query(News)
            
            # 应用来源过滤
            if source_filter:
                query = query.filter(News.source.ilike(f"%{source_filter}%"))
            
            # 应用排序
            if sort_by == "smart":
                # 智能排序：按综合评分降序
                query = query.order_by(desc(News.score))
            elif sort_by == "time":
                # 时间排序：按发布时间降序
                query = query.order_by(desc(News.published_at))
            elif sort_by == "headlines":
                # 点赞数排序：按点赞数降序
                query = query.order_by(desc(News.headline_count))
            else:
                # 默认使用智能排序
                query = query.order_by(desc(News.score))
            
            # 应用分页
            news_items = query.offset(offset).limit(limit).all()
            
            # 转换为字典格式
            results = []
            for item in news_items:
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
                
                results.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "summary": item.summary,
                    "link": item.link,
                    "date": date_str,
                    "source": item.source,
                    "published_at": date_str,
                    "summary_ai": item.summary_ai or {},
                    "headline_count": item.headline_count,
                    "keywords": item.keywords or [],
                    "score": item.score,
                    "vote_count": self.get_vote_count(item.title)
                })
            
            # 设置缓存，120秒
            redis_client.setex(cache_key, 120, json.dumps(results, ensure_ascii=False))
            return results
        except Exception as e:
            print(f"Error getting news: {e}")
            return []

    # 保存新闻
    def save_news(self, news_items: List[Dict]) -> bool:
        """保存新闻到数据库，包含智能评分"""
        try:
            # 获取现有新闻的关键词映射
            existing_news = self.get_news(0, 1000, "time")
            existing_keyword_map = build_existing_keyword_map(existing_news)
            
            for item in news_items:
                # 检查是否已存在
                existing = self.db.query(News).filter(News.title == item["title"]).first()
                if existing:
                    continue
                
                # 提取关键词
                keywords = extract_keywords_from_text(item["title"] + " " + item["content"])
                
                # 标准化日期处理
                raw_date = item.get("date", "")
                try:
                    if isinstance(raw_date, str):
                        # 解析RSS日期字符串并转换为UTC时间
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
                    print(f"Error parsing date '{raw_date}': {e}")
                    normalized_date = datetime.utcnow()
                
                # 创建AI摘要结构
                summary_ai = {
                    "brief": "",
                    "detailed": "",
                    "structure_score": 3.0  # 默认评分
                }
                
                # 计算综合评分
                score = calculate_news_score(
                    published_at=normalized_date,
                    summary_ai=summary_ai,
                    source=item.get("source", ""),
                    keywords=keywords,
                    headline_count=0,  # 新新闻初始点赞数为0
                    existing_keyword_map=existing_keyword_map
                )
                
                # 创建新闻对象
                news = News(
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
                    score=score
                )
                
                self.db.add(news)
            
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error saving news: {e}")
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