# backend/app/routes/news.py

from fastapi import APIRouter
from backend.news.fetch_news import get_tech_news
from backend.news.summarize import summarize_news, score_news
from urllib.parse import urlparse

router = APIRouter()

# 现在再定义 get_today_news 路由
@router.get("/news/today")
def get_today_news(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("smart", regex="^(smart|time|popular|ai_quality|source)$"),
    source_filter: str = Query(None)
):
    # 简化处理：使用默认限制
    max_limit = 100
    limit = min(limit, max_limit)

    raw = get_tech_news()
    results = []
    
    for item in raw:
        source = item.get("source") or urlparse(item["link"]).netloc.replace("www.", "")
        
        # 应用来源筛选
        if source_filter and source_filter.lower() not in source.lower():
            continue
            
        vote = db.query(Vote).filter(Vote.title == item["title"]).first()
        vote_count = vote.count if vote is not None else 0

        content = item.get("content") or item.get("summary") or ""
        summary = get_first_n_words(content, 600)
        
        # 获取AI评分
        ai_score = score_news(content) if content else 5

        # 计算综合评分
        comprehensive_score = calculate_comprehensive_score(item, vote_count, ai_score)

        results.append({
            "title": item["title"],
            "content": content,
            "summary": summary,
            "link": item["link"],
            "date": item["date"],
            "source": source,
            "vote_count": vote_count,
            "ai_score": ai_score,
            "comprehensive_score": comprehensive_score
        })
    
    # 根据排序方式排序
    if sort_by == "smart":
        # 智能综合排序（默认）
        results.sort(key=lambda x: x["comprehensive_score"], reverse=True)
    elif sort_by == "time":
        # 最新发布
        results.sort(key=lambda x: x["date"], reverse=True)
    elif sort_by == "popular":
        # 热门收藏
        results.sort(key=lambda x: x["vote_count"], reverse=True)
    elif sort_by == "ai_quality":
        # AI精选
        results.sort(key=lambda x: x["ai_score"], reverse=True)
    elif sort_by == "source":
        # 按来源权重排序
        results.sort(key=lambda x: SOURCE_WEIGHTS.get(x["source"], 0), reverse=True)
    
    return results[offset:offset+limit]