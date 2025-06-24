# backend/app/news/fetch_news.py

import feedparser
from typing import List, Dict
from datetime import datetime, timedelta
from dateutil import parser as dateparser

# 支持多个 RSS 源
RSS_FEEDS = {
    "BBC": "https://feeds.bbci.co.uk/news/rss.xml",
    "CNN": "https://rss.cnn.com/rss/edition.rss",
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "NYTimes": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Bloomberg": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    "AP News": "https://apnews.com/rss/apf-topnews",
    "NPR": "https://feeds.npr.org/1001/rss.xml",
    "Financial Times": "https://www.ft.com/?format=rss",
    "Fox News": "https://feeds.foxnews.com/foxnews/latest",
    "Sky News": "https://feeds.skynews.com/feeds/rss/world.xml",
}

def get_tech_news() -> List[Dict]:
    items = []
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                # 尝试解析日期
                raw_date = getattr(entry, "published", "") or getattr(entry, "updated", "")
                try:
                    published_dt = dateparser.parse(raw_date)
                except Exception:
                    continue  # 跳过无法解析日期的条目

                # 只保留一天之内的新闻
                if published_dt.tzinfo:
                    published_dt = published_dt.astimezone(tz=None).replace(tzinfo=None)
                if published_dt < one_day_ago:
                    continue

                content = ""
                if hasattr(entry, "content") and entry.content:
                    content = entry.content[0].value
                else:
                    content = getattr(entry, "summary", "")

                items.append({
                    "title": entry.title,
                    "summary": content[:2000],
                    "link": entry.link,
                    "date": raw_date,
                    "source": source_name
                })
        except Exception as e:
            print(f"[error] Failed to fetch {source_name}: {e}")
    # 最后加上全局排序
    items.sort(key=lambda x: dateparser.parse(x["date"]), reverse=True)
    return items