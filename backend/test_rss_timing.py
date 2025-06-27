#!/usr/bin/env python3
"""
测试RSS源的时间更新情况
"""

import feedparser
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from dateutil import tz
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RSS源配置
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

def test_rss_timing():
    """测试RSS源的时间更新情况"""
    now = datetime.utcnow()
    print(f"当前UTC时间: {now}")
    print(f"24小时前: {now - timedelta(hours=24)}")
    print(f"6小时前: {now - timedelta(hours=6)}")
    print("=" * 80)
    
    all_articles = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            print(f"\n📰 检查 {source_name}...")
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                print(f"  ❌ 没有找到文章")
                continue
                
            source_articles = []
            for i, entry in enumerate(feed.entries[:5]):  # 只检查前5篇文章
                # 尝试解析日期
                raw_date = getattr(entry, "published", "") or getattr(entry, "updated", "")
                
                if not raw_date:
                    print(f"  ⚠️  文章 {i+1}: 没有日期信息")
                    continue
                    
                try:
                    published_dt = dateparser.parse(raw_date)
                    
                    # 正确处理时区：转换为UTC进行比较
                    if published_dt.tzinfo:
                        published_dt_utc = published_dt.astimezone(tz.tzutc())
                    else:
                        published_dt_utc = published_dt.replace(tzinfo=tz.tzutc())
                    
                    # 计算时间差
                    time_diff = now - published_dt_utc.replace(tzinfo=None)
                    hours_ago = time_diff.total_seconds() / 3600
                    
                    article_info = {
                        "source": source_name,
                        "title": str(entry.title)[:50] + "..." if len(str(entry.title)) > 50 else str(entry.title),
                        "published": published_dt_utc,
                        "hours_ago": hours_ago,
                        "raw_date": raw_date
                    }
                    
                    source_articles.append(article_info)
                    
                    status = "✅" if hours_ago <= 24 else "❌"
                    print(f"  {status} 文章 {i+1}: {hours_ago:.1f}小时前 - {entry.title[:50]}...")
                    
                except Exception as e:
                    print(f"  ❌ 文章 {i+1}: 日期解析失败 - {raw_date} - {e}")
                    continue
            
            if source_articles:
                # 找到该源最新的文章
                latest_article = min(source_articles, key=lambda x: x["hours_ago"])
                all_articles.append(latest_article)
                print(f"  📊 最新文章: {latest_article['hours_ago']:.1f}小时前")
            else:
                print(f"  ❌ 没有有效文章")
                
        except Exception as e:
            print(f"  ❌ 获取失败: {e}")
    
    print("\n" + "=" * 80)
    print("📊 汇总报告:")
    
    if all_articles:
        # 按时间排序
        all_articles.sort(key=lambda x: x["hours_ago"])
        
        print(f"\n最新文章 (前10):")
        for i, article in enumerate(all_articles[:10]):
            print(f"  {i+1}. {article['source']}: {article['hours_ago']:.1f}小时前 - {article['title']}")
        
        # 统计信息
        recent_articles = [a for a in all_articles if a["hours_ago"] <= 6]
        recent_24h = [a for a in all_articles if a["hours_ago"] <= 24]
        
        print(f"\n📈 统计:")
        print(f"  6小时内: {len(recent_articles)}/{len(all_articles)} 个源")
        print(f"  24小时内: {len(recent_24h)}/{len(all_articles)} 个源")
        print(f"  平均更新时间: {sum(a['hours_ago'] for a in all_articles) / len(all_articles):.1f}小时前")
        
        if recent_articles:
            print(f"  ✅ 有 {len(recent_articles)} 个源在6小时内更新")
        else:
            print(f"  ⚠️  没有源在6小时内更新，建议检查RSS源或调整时间过滤")
    else:
        print("❌ 没有获取到任何有效文章")

if __name__ == "__main__":
    test_rss_timing() 