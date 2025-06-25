import schedule
import time
from cache_worker import refresh_news_cache

def job():
    print("Refreshing news cache...")
    refresh_news_cache()

schedule.every(15).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
