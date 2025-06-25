from fastapi import APIRouter, Depends, Query, Body, HTTPException, Header
from sqlalchemy.orm import Session
from news.fetch_news import get_tech_news
from backend.db import SessionLocal
from models import Vote, User
from urllib.parse import urlparse
import os
from openai import OpenAI
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_first_n_words(text: str, n: int) -> str:
    """获取文本的前n个单词"""
    if not text:
        return ""
    words = text.split()
    return " ".join(words[:n])

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
        email = idinfo["email"]
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, is_subscribed=False)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# 来源权重配置
SOURCE_WEIGHTS = {
    "Financial Times": 1.0,
    "Wall Street Journal": 1.0,
    "The Economist": 1.0,
    "Reuters": 0.9,
    "Bloomberg": 0.9,
    "BBC": 0.8,
    "CNN": 0.8,
    "The New York Times": 0.8,
    "The Washington Post": 0.8,
    "The Guardian": 0.7,
    "TechCrunch": 0.6,
    "Ars Technica": 0.6,
    "Wired": 0.6,
    "The Verge": 0.5,
    "Engadget": 0.5,
    "Mashable": 0.4,
    "Gizmodo": 0.4,
}

def calculate_comprehensive_score(item, vote_count, ai_score):
    """计算综合评分"""
    from datetime import datetime, timedelta
    
    # 1. 时间因子 (0-1, 越新越高)
    try:
        pub_date = datetime.fromisoformat(item["date"].replace('Z', '+00:00'))
        now = datetime.now(pub_date.tzinfo)
        hours_ago = (now - pub_date).total_seconds() / 3600
        
        if hours_ago <= 12:
            time_factor = 1.0 - (hours_ago / 12) * 0.3  # 12小时内，最高1.0，最低0.7
        elif hours_ago <= 24:
            time_factor = 0.7 - ((hours_ago - 12) / 12) * 0.3  # 24小时内，0.7到0.4
        else:
            time_factor = max(0.1, 0.4 - (hours_ago - 24) / 24 * 0.3)  # 超过24小时，最低0.1
    except:
        time_factor = 0.5  # 解析失败时使用默认值
    
    # 2. 来源权重 (0-1)
    source = item.get("source", "")
    source_weight = SOURCE_WEIGHTS.get(source, 0.3)  # 默认权重0.3
    
    # 3. AI质量分 (0-1)
    ai_quality = (ai_score or 5) / 10.0  # 转换为0-1
    
    # 4. 热度因子 (0-1)
    # 基于投票数，使用对数函数避免极端值
    popularity_factor = min(1.0, (vote_count + 1) / 10.0)  # 0-1，10票以上算满分
    
    # 综合评分公式
    comprehensive_score = (
        time_factor * 0.5 +      # 时间权重50%
        source_weight * 0.2 +    # 来源权重20%
        ai_quality * 0.2 +       # AI质量权重20%
        popularity_factor * 0.1  # 热度权重10%
    )
    
    return comprehensive_score

# 现在再定义 get_today_news 路由
@router.get("/news/today")
def get_today_news(
    db: Session = Depends(get_db),
    user: User = None,  # 临时设为可选
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("smart", regex="^(smart|time|popular|ai_quality|source)$"),
    source_filter: str = Query(None)
):
    # 临时处理：如果没有用户，使用默认限制
    max_limit = 100 if user and user.is_subscribed else 20
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

@router.post("/news/vote")
def vote_news(
    title: str = Query(...),
    delta: int = Query(1),
    db: Session = Depends(get_db)
):
    vote = db.query(Vote).filter(Vote.title == title).first()
    if vote is not None:
        vote.count = vote.count + delta
    else:
        vote = Vote(title=title, count=delta)
        db.add(vote)
    db.commit()
    db.refresh(vote)
    return {"count": vote.count}

@router.get("/news/vote")
def get_vote(title: str = Query(...), db: Session = Depends(get_db)):
    vote = db.query(Vote).filter(Vote.title == title).first()
    return {"count": vote.count if vote else 0}

@router.post("/news/summary")
def news_summary(data: dict = Body(...)):
    text = data.get("content", "")
    print(f"🔍 [DEBUG] Received content length: {len(text)}")
    print(f"🔍 [DEBUG] Content preview: {text[:200]}...")
    print(f"🔍 [DEBUG] Content is empty: {not text.strip()}")
    return {"summary": summarize_news(text, 300)}

@router.get("/news/score")
def news_score(text: str = Query(...)):
    # 独立打分接口，返回 1-10 分
    score = score_news(text)
    return {"ai_score": score}

@router.get("/news/article")
def get_article_by_title(title: str = Query(...)):
    """根据标题获取文章详情"""
    raw = get_tech_news()
    for item in raw:
        if item["title"] == title:
            source = item.get("source") or urlparse(item["link"]).netloc.replace("www.", "")
            content = item.get("content") or item.get("summary") or ""
            
            return {
                "id": item.get("id", ""),
                "title": item["title"],
                "content": content,
                "link": item["link"],
                "date": item["date"],
                "source": source
            }
    
    raise HTTPException(status_code=404, detail="Article not found")

@router.get("/news/article/{article_id}")
def get_article_by_id(article_id: str):
    """根据ID获取文章详情"""
    raw = get_tech_news()
    for item in raw:
        if str(item.get("id", "")) == article_id:
            source = item.get("source") or urlparse(item["link"]).netloc.replace("www.", "")
            content = item.get("content") or item.get("summary") or ""
            
            return {
                "id": item.get("id", ""),
                "title": item["title"],
                "content": content,
                "link": item["link"],
                "date": item["date"],
                "source": source
            }
    
    raise HTTPException(status_code=404, detail="Article not found")

def summarize_news(text: str, word_count: int = 70) -> str:
    print(f"🤖 [DEBUG] summarize_news called with text length: {len(text)}")
    print(f"🤖 [DEBUG] Text preview: {text[:300]}...")
    
    if not text.strip():
        print("❌ [ERROR] Empty text passed to summarize_news!")
        return "No content available for summarization"
    
    prompt = (
        "Read the whole article and summarize this news in at least 420 characters "
        "and more than 65 words. Be as detailed as possible. Do not just copy and paste content."
        "Do not mention the source, outlet, or 'the article'. Just summarize the core content.\n\n"
        f"{text}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=word_count * 2,
            temperature=0.5,
        )
        content = resp.choices[0].message.content
        result = content.strip() if content else "generation failed"
        print(f"✅ [DEBUG] Generated summary: {result[:100]}...")
        return result
    except Exception as e:
        print(f"❌ [ERROR] OpenAI summarize error: {e}")
        return "generation failed"


def score_news(text: str) -> int:
    """
    用 GPT 给新闻打分（1-10分），分数越高代表越有价值/可读性。
    """
    prompt = (
    "You are an experienced journalist working for a major international news outlet like BBC or CNN.\n"
    "Please read the following news article and give it an importance score from 1 to 10,\n"
    "where 10 means extremely important and globally relevant, and 1 means very minor or trivial.\n\n"
    "Consider factors such as:\n"
    "- Global political or economic impact\n"
    "- Urgency and timeliness\n"
    "- Public interest and relevance\n"
    "- Societal consequences\n"
    "- Scope of affected population\n\n"
    "Respond with a single integer only, no explanation.\n\n"
        f"{text}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.2,
        )
        score_str = resp.choices[0].message.content.strip() if resp.choices[0].message.content else "5"
        score = int(''.join(filter(str.isdigit, score_str)))
        return max(1, min(score, 10))
    except Exception as e:
        print("OpenAI score error:", e)
        return 5  # 返回默认分数而不是None