from sqlalchemy.orm import Session
from app.models import News, Vote
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict

class PostgresService:
    def __init__(self, db: Session):
        self.db = db

    # 获取新闻
    def get_news(self, offset=0, limit=20, sort_by="time", source_filter=None) -> List[News]:
        query = self.db.query(News)

        if source_filter:
            query = query.filter(News.source.ilike(f"%{source_filter}%"))

        # 排序
        if sort_by == "time":
            query = query.order_by(News.date.desc())
        else:  # 默认使用时间排序
            query = query.order_by(News.date.desc())

        return query.offset(offset).limit(limit).all()

    # 保存新闻
    def save_news(self, news_items: List[Dict]) -> bool:
        try:
            # 清空旧新闻
            self.db.query(News).delete()
            for item in news_items:
                news = News(
                    title=item["title"],
                    content=item["content"],
                    summary=item.get("summary", ""),
                    link=item["link"],
                    date=item.get("date", datetime.utcnow()),
                    source=item.get("source", "")
                )
                self.db.add(news)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error saving news: {e}")
            return False

    # 获取投票数
    def get_vote_count(self, title: str) -> int:
        vote = self.db.query(Vote).filter(Vote.title == title).first()
        return int(getattr(vote, "count", 0)) if vote else 0

    # 更新投票
    def update_vote(self, title: str, delta: int) -> int:
        vote = self.db.query(Vote).filter(Vote.title == title).first()
        if not vote:
            vote = Vote(title=title, count=delta)
            self.db.add(vote)
        else:
            setattr(vote, "count", int(getattr(vote, "count", 0)) + delta)
        self.db.commit()
        return int(getattr(vote, "count", 0)) 