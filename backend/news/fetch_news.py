# backend/app/news/fetch_news.py

import feedparser
from typing import List, Dict
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from dateutil import tz
import logging

logger = logging.getLogger(__name__)

# 支持多个 RSS 源
RSS_FEEDS = {
    # 美国主流媒体
    "The New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "The Washington Post": "https://feeds.washingtonpost.com/rss/national",
    "Los Angeles Times": "https://www.latimes.com/local/rss2.0.xml",
    "NBC News": "https://feeds.nbcnews.com/nbcnews/public/world",
    "CBS News": "https://www.cbsnews.com/latest/rss/main",
    "ABC News": "https://feeds.abcnews.com/abcnews/usheadlines",
    "Fox News": "https://feeds.foxnews.com/foxnews/latest",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Axios": "https://api.axios.com/feed/",
    
    # 国际新闻机构
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "Associated Press": "https://apnews.com/rss/apf-topnews",
    "Bloomberg": "https://feeds.bloomberg.com/politics/news.rss",
    
    # 英国媒体
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "The Telegraph": "https://www.telegraph.co.uk/rss.xml",
    "Financial Times": "https://www.ft.com/?format=rss",
    "Sky News": "https://feeds.skynews.com/feeds/rss/world.xml",
    "The Independent": "https://www.independent.co.uk/news/world/rss",
    
    # 欧洲媒体
    "Euronews": "https://www.euronews.com/rss?format=mrss&level=theme&name=news",
    "Deutsche Welle": "https://rss.dw.com/xml/rss-de-all",
    
    # 中东媒体
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
}

def get_tech_news(force_refresh: bool = False) -> List[Dict]:
    """
    获取新闻，直接从RSS获取
    """
    logger.info("Fetching fresh news from RSS feeds...")
    return fetch_from_rss()

def fetch_from_rss() -> List[Dict]:
    """从RSS源获取新闻"""
    items = []
    now = datetime.utcnow()
    six_hours_ago = now - timedelta(hours=6)

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

                # 正确处理时区：转换为UTC进行比较
                if published_dt.tzinfo:
                    # 如果有时区信息，转换为UTC
                    published_dt_utc = published_dt.astimezone(tz.tzutc())
                else:
                    # 如果没有时区信息，假设是UTC
                    published_dt_utc = published_dt.replace(tzinfo=tz.tzutc())
                
                # 只保留6小时之内的新闻
                if published_dt_utc.replace(tzinfo=None) < six_hours_ago:
                    continue

                # 优化内容获取逻辑
                content = ""
                summary = ""
                
                # 1. 优先获取完整内容
                if hasattr(entry, "content") and entry.content:
                    content = entry.content[0].value
                    logger.debug(f"{source_name} - Using content field, length: {len(content)}")
                # 2. 如果没有content，尝试获取summary
                elif hasattr(entry, "summary") and entry.summary:
                    content = entry.summary
                    logger.debug(f"{source_name} - Using summary as content, length: {len(content)}")
                # 3. 如果都没有，跳过这条新闻
                else:
                    logger.warning(f"{source_name} - No content or summary found for: {entry.title}")
                    continue
                
                # 确保内容不为空
                if not content or not str(content).strip():
                    logger.warning(f"{source_name} - Empty content for: {entry.title}")
                    continue
                
                # 创建摘要（用于显示）
                summary = content[:600] if len(content) > 600 else content

                # 格式化日期为ISO字符串
                formatted_date = published_dt_utc.isoformat()

                items.append({
                    "title": entry.title,
                    "content": content,  # 完整内容用于AI摘要
                    "summary": summary,  # 简短摘要用于显示
                    "link": entry.link,
                    "date": formatted_date,  # 使用格式化的ISO日期字符串
                    "source": source_name
                })
                
                logger.debug(f"{source_name} - Added article: {entry.title[:50]}... (content: {len(content)} chars)")
                
        except Exception as e:
            logger.error(f"Failed to fetch {source_name}: {e}")
    
    logger.info(f"Total articles fetched from RSS: {len(items)}")
    # 最后加上全局排序
    items.sort(key=lambda x: dateparser.parse(x["date"]), reverse=True)
    return items
