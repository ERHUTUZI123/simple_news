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

                # 优化内容获取逻辑
                content = ""
                summary = ""
                
                # 1. 优先获取完整内容
                if hasattr(entry, "content") and entry.content:
                    content = entry.content[0].value
                    print(f"📰 [DEBUG] {source_name} - Using content field, length: {len(content)}")
                # 2. 如果没有content，尝试获取summary
                elif hasattr(entry, "summary") and entry.summary:
                    content = entry.summary
                    print(f"📰 [DEBUG] {source_name} - Using summary as content, length: {len(content)}")
                # 3. 如果都没有，跳过这条新闻
                else:
                    print(f"⚠️ [WARNING] {source_name} - No content or summary found for: {entry.title}")
                    continue
                
                # 确保内容不为空
                if not content or not str(content).strip():
                    print(f"⚠️ [WARNING] {source_name} - Empty content for: {entry.title}")
                    continue
                
                # 创建摘要（用于显示）
                summary = content[:600] if len(content) > 600 else content

                items.append({
                    "title": entry.title,
                    "content": content,  # 完整内容用于AI摘要
                    "summary": summary,  # 简短摘要用于显示
                    "link": entry.link,
                    "date": raw_date,
                    "source": source_name
                })
                
                print(f"✅ [DEBUG] {source_name} - Added article: {entry.title[:50]}... (content: {len(content)} chars)")
                
        except Exception as e:
            print(f"[error] Failed to fetch {source_name}: {e}")
    
    print(f"📊 [DEBUG] Total articles fetched: {len(items)}")
    # 最后加上全局排序
    items.sort(key=lambda x: dateparser.parse(x["date"]), reverse=True)
    return items
