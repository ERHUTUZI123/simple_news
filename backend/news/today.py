# backend/app/routes/news.py

from fastapi import APIRouter
from app.news.fetch_news import get_tech_news
from app.news.summarize import summarize_news, score_news
from urllib.parse import urlparse

router = APIRouter()

@router.get("/news/today")
def get_today_news():
    raw = get_tech_news()
    results = []
    for item in raw:
        # 优先用 content，没有就用 summary
        content = item.get("content", "") or item.get("summary", "")
        ai_summary = summarize_news(content, 120)  # 你可以调整 word_count
        # 直接返回更长的内容，不再二次 summarize，summary 字段直接给前端
        score = score_news(content)
        source = item.get("source") or urlparse(item["link"]).netloc.replace("www.", "")
        results.append({
            "title": item["title"],
            "summary": ai_summary,
            "link": item["link"],
            "date": item["date"],
            "score": score,
            "source": source
        })
    return results

# backend/app/news/fetch_news.py

for entry in feed.entries[:10]:
    content = ""
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].value
    else:
        content = getattr(entry, "summary", "")
    # ...
    items.append({
        "title": entry.title,
        "summary": content[:2000],  # 让 summary 字段更长
        # ...
    })
