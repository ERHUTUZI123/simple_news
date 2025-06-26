from fastapi import APIRouter, Depends, Query, Body, HTTPException, Header
from sqlalchemy.orm import Session
from app.news.postgres_service import PostgresService
from app.db import SessionLocal
from news.fetch_news import get_tech_news
from urllib.parse import urlparse
import os
from openai import OpenAI
from dotenv import load_dotenv
import time
import random
from typing import Optional

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

# 速率限制配置
RATE_LIMIT_DELAY = 2.0  # 基础延迟时间（秒）
MAX_RETRIES = 3  # 最大重试次数

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

def get_pg_service():
    db = SessionLocal()
    try:
        yield PostgresService(db)
    finally:
        db.close()

def get_first_n_words(text: str, n: int) -> str:
    """获取文本的前n个单词"""
    if not text:
        return ""
    words = text.split()
    return " ".join(words[:n])

@router.get("/news/today")
def get_today_news(
    pg_service: PostgresService = Depends(get_pg_service),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("time"),  # 可以支持 smart/time/ai_quality
    source_filter: str = Query(None)
):
    # 获取 Postgres 的新闻
    news_items = pg_service.get_news(offset, limit, sort_by, source_filter)
    if not news_items:
        # 如果没数据，抓取 RSS 并存入
        raw = get_tech_news(force_refresh=True)
        pg_service.save_news(raw)
        news_items = pg_service.get_news(offset, limit, sort_by, source_filter)
    results = []
    for item in news_items:
        title_str = str(getattr(item, 'title', ''))
        date_str = str(getattr(item, 'date', ''))
        vote_count = pg_service.get_vote_count(title_str)
        results.append({
            "title": title_str,
            "content": item.content,
            "summary": item.summary,
            "link": item.link,
            "date": date_str,
            "source": item.source,
            "vote_count": vote_count,
            "ai_score": item.ai_score,
        })
    return results

@router.post("/news/vote")
def vote_news(
    title: str = Query(...),
    delta: int = Query(1),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """投票接口"""
    new_count = pg_service.update_vote(title, delta)
    return {"count": new_count}

@router.get("/news/vote")
def get_vote(
    title: str = Query(...),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """获取投票数"""
    count = pg_service.get_vote_count(title)
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
def get_article_by_title(
    title: str = Query(...),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """根据标题获取文章"""
    news_items = pg_service.get_news(0, 1000)
    for item in news_items:
        title_str = str(getattr(item, 'title', ''))
        if title_str == title:
            return {
                "title": title_str,
                "content": item.content,
                "summary": item.summary,
                "link": item.link,
                "date": str(getattr(item, 'date', '')),
                "source": item.source,
                "vote_count": pg_service.get_vote_count(title_str),
                "ai_score": item.ai_score,
            }
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
    """评分新闻重要性，返回1-10分"""
    if not text.strip():
        print("❌ [ERROR] Empty text passed to score_news!")
        return 5
    
    prompt = (
        "Please rate the significance of this news article (1–10):\n\n"
        "Consider the scale and extent of impact.\n\n"
        "Prioritize international politics, economics, and technological changes.\n"
        "(1 = minor significance; 10 = extremely significant)\n\n"
        f"{text[:1000]}..."
    )
    try:
        result = _call_openai_score(prompt)
        print(f"[DEBUG] OpenAI score raw result: {result}")
        if result:
            import re
            numbers = re.findall(r'\d+', result)
            if numbers:
                score = int(numbers[0])
                print(f"[DEBUG] Parsed score: {score}")
                return max(1, min(10, score))
            else:
                print("[ERROR] No number found in OpenAI response!")
        else:
            print("[ERROR] OpenAI returned empty result!")
    except Exception as e:
        print(f"❌ [ERROR] Score parsing error: {e}")
    return 5  # 默认分数