from fastapi import APIRouter, Depends, Query, Body, HTTPException, Header
from sqlalchemy.orm import Session
from news.fetch_news import get_tech_news
from news.db import SessionLocal
from news.mongo_service import MongoService
from models import Vote, User
from urllib.parse import urlparse
import os
from openai import OpenAI
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import time
import random
from typing import Optional

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

# 速率限制配置
RATE_LIMIT_DELAY = 2.0  # 基础延迟时间（秒）
MAX_RETRIES = 3  # 最大重试次数

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mongo_service():
    """获取 MongoDB 服务实例"""
    return MongoService()

def get_first_n_words(text: str, n: int) -> str:
    """获取文本的前n个单词"""
    if not text:
        return ""
    words = text.split()
    return " ".join(words[:n])

def get_current_user(
    authorization: str = Header(None),
    mongo_service: MongoService = Depends(get_mongo_service)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
        email = idinfo["email"]
        user = mongo_service.get_user(email)
        if not user:
            mongo_service.create_user(email, is_subscribed=False)
            user = mongo_service.get_user(email)
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

def handle_openai_rate_limit(func):
    """装饰器：处理OpenAI速率限制"""
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e)
                if "rate_limit" in error_str.lower() or "429" in error_str:
                    if attempt < MAX_RETRIES - 1:
                        # 计算延迟时间：基础延迟 + 随机抖动
                        delay = RATE_LIMIT_DELAY + random.uniform(0, 1)
                        print(f"⚠️ [RATE_LIMIT] Attempt {attempt + 1} failed, retrying in {delay:.2f}s...")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"❌ [RATE_LIMIT] Max retries reached, returning default value")
                        return None
                else:
                    # 非速率限制错误，直接抛出
                    raise e
        return None
    return wrapper

# 现在再定义 get_today_news 路由
@router.get("/news/today")
def get_today_news(
    mongo_service: MongoService = Depends(get_mongo_service),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("smart", regex="^(smart|time|popular|ai_quality|source)$"),
    source_filter: str = Query(None)
):
    # 简化处理：使用默认限制
    max_limit = 100
    limit = min(limit, max_limit)

    # 从 MongoDB 获取新闻
    news_items = mongo_service.get_news(offset, limit, sort_by, source_filter)
    
    # 如果没有缓存的新闻，从 RSS 获取并存入 MongoDB
    if not news_items:
        raw = get_tech_news(force_refresh=True)
        mongo_service.save_news(raw)  # ✅ 保存抓取结果到 MongoDB
        news_items = mongo_service.get_news(offset, limit, sort_by, source_filter)
    
    results = []
    
    for item in news_items:
        source = item.get("source") or urlparse(item["link"]).netloc.replace("www.", "")
        
        # 应用来源筛选
        if source_filter and source_filter.lower() not in source.lower():
            continue
            
        # 从 MongoDB 获取投票数
        vote_count = mongo_service.get_vote_count(item["title"])

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
        # AI质量排序
        results.sort(key=lambda x: x["ai_score"], reverse=True)
    
    return results

@router.post("/news/vote")
def vote_news(
    title: str = Query(...),
    delta: int = Query(1),
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """投票接口"""
    new_count = mongo_service.update_vote(title, delta)
    return {"count": new_count}

@router.get("/news/vote")
def get_vote(title: str = Query(...), mongo_service: MongoService = Depends(get_mongo_service)):
    """获取投票数"""
    count = mongo_service.get_vote_count(title)
    return {"count": count}

@router.post("/news/summary")
def news_summary(data: dict = Body(...)):
    """生成新闻摘要"""
    content = data.get("content", "")
    summary = summarize_news(content)
    return {"summary": summary}

@router.get("/news/score")
def news_score(text: str = Query(...)):
    """独立打分接口，返回 1-10 分"""
    score = score_news(text)
    return {"ai_score": score}

@router.get("/news/article")
def get_article_by_title(title: str = Query(...)):
    """根据标题获取文章"""
    mongo_service = MongoService()
    news_items = mongo_service.get_news(0, 1000)  # 获取所有新闻
    
    for item in news_items:
        if item["title"] == title:
            return item
    
    return {"error": "Article not found"}

@router.get("/news/article/{article_id}")
def get_article_by_id(article_id: str):
    """根据ID获取文章（兼容性接口）"""
    # 这里可以根据需要实现具体的逻辑
    return {"error": "Article not found"}

@handle_openai_rate_limit
def _call_openai_summarize(prompt: str, max_tokens: int) -> Optional[str]:
    """调用OpenAI生成摘要"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ [ERROR] OpenAI summarize error: {e}")
        return None

@handle_openai_rate_limit
def _call_openai_score(prompt: str) -> Optional[str]:
    """调用OpenAI评分"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ [ERROR] OpenAI score error: {e}")
        return None

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
        content = _call_openai_summarize(prompt, word_count * 2)
        if content is None:
            print("❌ [ERROR] OpenAI call failed due to rate limiting")
            return "Summary generation temporarily unavailable due to high demand"
        
        result = content.strip() if content else "generation failed"
        print(f"✅ [DEBUG] Generated summary: {result[:100]}...")
        return result
    except Exception as e:
        print(f"❌ [ERROR] OpenAI summarize error: {e}")
        return "generation failed"

def score_news(text: str) -> int:
    """评分新闻质量，返回1-10分"""
    if not text.strip():
        return 5
    
    prompt = (
        "Rate the quality and newsworthiness of this news article on a scale of 1-10. "
        "Consider factors like accuracy, relevance, depth, and journalistic quality. "
        "Respond with only the number (1-10).\n\n"
        f"Article: {text[:1000]}..."
    )
    
    try:
        result = _call_openai_score(prompt)
        if result:
            # 提取数字
            import re
            numbers = re.findall(r'\d+', result)
            if numbers:
                score = int(numbers[0])
                return max(1, min(10, score))  # 确保在1-10范围内
    except Exception as e:
        print(f"❌ [ERROR] Score parsing error: {e}")
    
    return 5  # 默认分数