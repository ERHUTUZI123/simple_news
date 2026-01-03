# backend/app/news/fetch_news.py
# feedparser parsing principles for rss items:
# feed = feedparser.parse(rss_source)
# feed.entries
# ├─ entry[0]
# │   ├─ entry.title
# │   ├─ entry.summary
# │   ├─ entry.content
# │   └─ entry.link
# ├─ entry[1]
# └─ entry[2]
# <title> </title> => feed.entry[x].title
# <link> </link>
# <pubDate> </pubDate> => feed.published


# feedparser can parse RSS and Atom feeds 
import feedparser
# List and Dict helps specify List and Dict expected
#  data types 
from typing import List, Dict
# datetime is for current time and timedelta is
#  for time differences
from datetime import datetime, timedelta
# parser is used to convert data strings into Python datetime objects
from dateutil import parser as dateparser
# tz is used for timezone handling
from dateutil import tz
# logging module is used to record events and errors
import logging
from bs4 import BeautifulSoup
import requests
from news_readers import nyc

# create a logger
# write .getLogger(__name__) to let logs show their origins
logger = logging.getLogger(__name__)

# support multi RSS
# define a dict to store rss feeds
# allow code to fetch news by looping through the dict
# divide them into groups
RSS_FEEDS = {
    # American top meida
    "The New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "The Washington Post": "https://feeds.washingtonpost.com/rss/national",
    "Los Angeles Times": "https://www.latimes.com/local/rss2.0.xml",
    "NBC News": "https://feeds.nbcnews.com/nbcnews/public/world",
    "CBS News": "https://www.cbsnews.com/latest/rss/main",
    "ABC News": "https://feeds.abcnews.com/abcnews/usheadlines",
    "Fox News": "https://feeds.foxnews.com/foxnews/latest",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Axios": "https://api.axios.com/feed/",
    "Bloomberg": "https://feeds.bloomberg.com/politics/news.rss",
    "Associated Press": "https://apnews.com/rss/apf-topnews",

    # International media
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "CGTN": "https://www.cgtn.com/subscribe/rss/section/world.xml",
    "Russai Today": "https://www.rt.com/rss/news/",

    # British media
    "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "The Telegraph": "https://www.telegraph.co.uk/rss.xml",
    "Financial Times": "https://www.ft.com/?format=rss",
    "Sky News": "https://feeds.skynews.com/feeds/rss/world.xml",
    "The Independent": "https://www.independent.co.uk/news/world/rss",
    
    # Euro meida
    "Euronews": "https://www.euronews.com/rss?format=mrss&level=theme&name=news",
    "Deutsche Welle": "https://rss.dw.com/xml/rss-de-all",
    
    # Middle east media
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
}

# define fetch_from_rss() which returns a list of news
def fetch_from_rss() -> List[Dict]:
    """
    fetch news from rss
    """
    # log that it is fetching news
    logger.info("Fetching fresh news from RSS feeds...")
    # initialize an empty list to store news
    items = []
    # gets the current utc time
    now = datetime.utcnow()
    # calculate the time 24 hrs ago to filter out old news
    twenty_four_hours_ago = dateparser.parse("24 hrs ago")
    # loop through each news source and its RSS URL
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            # parse feed URL
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                # parse raw date
                raw_date = (getattr(entry, "published", "") or 
                            getattr(entry, "updated", ""))
                try:
                    # define pubslished_at through parsing raw_date
                    published_dt = dateparser.parse(raw_date)
                except Exception:
                    # skip news that cannot be parsed
                    continue  

                # convert date to utc and make comparisons
                if published_dt.tzinfo:
                    # convert to utc if there is tz
                    published_dt_utc = published_dt.astimezone(tz.tzutc())
                else:
                    # assume to be utc if no tz info
                    published_dt_utc = published_dt.replace(tzinfo=tz.tzutc())
                
                # keep only news within 24 hrs
                if published_dt_utc.replace(tzinfo=None) < twenty_four_hours_ago:
                    continue

                # define content and summary
                news_url = str(getattr(entry, 'link'))
                # news is from bbc
                if news_url.startswith('https://www.bbc.com/news/articles/'):
                    article = soup.find_all('p', attrs={"class": "sc-9a00e533-0 eZyhnA"})
                    content = ""
                    for para in article:
                        soup = BeautifulSoup(str(para), 'html.parser')
                        text = soup.get_text(strip=True)
                        content += text
                # news is from nyc
                elif news_url.startswith('https://www.nytimes.com/'):
                    content = nyc.fetch_news(news_url)  
            
                # format date to ISO
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
