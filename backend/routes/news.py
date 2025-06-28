from fastapi import APIRouter, Depends, Query, Body, HTTPException, Header, Request
from sqlalchemy.orm import Session
from app.news.postgres_service import PostgresService
from app.db import SessionLocal
from news.fetch_news import get_tech_news
from news.summarize import generate_both_summaries, summarize_news
from urllib.parse import urlparse
import os
from openai import OpenAI
from dotenv import load_dotenv
import time
import random
from typing import Optional
from datetime import datetime, timedelta
from app.models import SavedArticle, User, News, Vote
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID
from sqlalchemy import func, desc

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

@router.get("/news")
def get_news(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    source: Optional[str] = Query(None),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """
    获取新闻列表，按时间排序（最新优先）
    """
    try:
        # 使用PostgresService获取新闻，按时间排序
        news_items = pg_service.get_news(offset, limit, "time", source)
        return {"news": news_items}
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
    """Generate news summary"""
    content = data.get("content", "")
    summary_type = data.get("type", "detailed")  # Default to detailed
    
    if summary_type == "both":
        # Generate both types of summaries
        result = generate_both_summaries(content)
        return result
    else:
        # Generate single type summary
        result = summarize_news(content, summary_type)
        return {"summary": result["summary"], "structure_score": result["structure_score"]}

@router.get("/news/article")
def get_article_by_title(
    title: str = Query(...),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """根据标题获取文章"""
    return pg_service.get_article_by_title(title)

@router.get("/news/article/{article_id}")
def get_article_by_id(article_id: str):
    """根据ID获取文章（兼容性接口）"""
    # 这里可以根据需要实现具体的逻辑
    return {"error": "Article not found"}

@router.post("/news/refresh")
def refresh_news(
    pg_service: PostgresService = Depends(get_pg_service)
):
    """手动刷新新闻"""
    try:
        # 抓取 RSS 并存入
        raw = get_tech_news(force_refresh=True)
        pg_service.save_news(raw)
        return {"message": "News refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh news: {str(e)}")

@router.get("/news/sources")
def get_news_sources(
    pg_service: PostgresService = Depends(get_pg_service)
):
    """获取所有新闻来源"""
    try:
        # 返回所有支持的新闻来源
        sources = [
            # 美国主流媒体
            "The New York Times", "The Washington Post", "Los Angeles Times", 
            "NBC News", "CBS News", "ABC News", "Fox News", "CNBC", "Axios",
            # 国际新闻机构
            "Reuters", "Associated Press", "Bloomberg",
            # 英国媒体
            "BBC News", "The Guardian", "The Telegraph", 
            "Financial Times", "Sky News", "The Independent",
            # 欧洲媒体
            "Euronews", "Deutsche Welle",
            # 中东媒体
            "Al Jazeera",
        ]
        return {"sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sources: {str(e)}")

@router.get("/news/sort-options")
def get_sort_options():
    """获取排序选项（已废弃，保留兼容性）"""
    return {
        "sort_options": [
            {"value": "time", "label": "Latest First"}
        ]
    }

@router.post("/api/save")
async def save_article(request: Request, pg_service: PostgresService = Depends(get_pg_service)):
    """保存文章"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        news_id = data.get("news_id")
        
        if not user_id or not news_id:
            raise HTTPException(status_code=400, detail="Missing user_id or news_id")
        
        # 检查用户是否存在，如果不存在则创建
        user = pg_service.get_user_by_id(user_id)
        if not user:
            user_data = data.get("user", {})
            user = pg_service.create_user(user_id, user_data.get("email"), user_data.get("name"))
        
        # 保存文章
        saved_article = pg_service.save_article(user_id, news_id)
        return {"message": "Article saved successfully", "saved_article": saved_article}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving article: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/api/save")
async def unsave_article(request: Request, pg_service: PostgresService = Depends(get_pg_service)):
    """取消保存文章"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        news_id = data.get("news_id")
        
        if not user_id or not news_id:
            raise HTTPException(status_code=400, detail="Missing user_id or news_id")
        
        pg_service.unsave_article(user_id, news_id)
        return {"message": "Article unsaved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error unsaving article: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/saved")
async def get_saved_articles(
    user_id: str = Query(...),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """获取用户保存的文章"""
    try:
        saved_articles = pg_service.get_saved_articles_for_user(user_id)
        return {"saved_articles": saved_articles}
        
    except Exception as e:
        print(f"Error getting saved articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/saved/check")
async def check_article_saved(
    user_id: str = Query(...),
    news_id: str = Query(...),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """检查文章是否已保存"""
    try:
        is_saved = pg_service.is_article_saved(user_id, news_id)
        return {"is_saved": is_saved}
        
    except Exception as e:
        print(f"Error checking saved article: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/auth/save-user")
async def save_user(request: Request, pg_service: PostgresService = Depends(get_pg_service)):
    """保存用户信息"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        email = data.get("email")
        name = data.get("name")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id")
        
        user = pg_service.create_user(user_id, email, name)
        return {"message": "User saved successfully", "user": user}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/news/clean-duplicates")
def clean_duplicate_news(pg_service: PostgresService = Depends(get_pg_service)):
    """清理重复新闻"""
    try:
        # 获取所有新闻
        all_news = pg_service.get_all_news()
        
        # 按标题分组，找出重复的
        title_groups = {}
        for news in all_news:
            title = news.get('title', '').strip().lower()
            if title:
                if title not in title_groups:
                    title_groups[title] = []
                title_groups[title].append(news)
        
        # 删除重复的新闻（保留最新的）
        deleted_count = 0
        for title, news_list in title_groups.items():
            if len(news_list) > 1:
                # 按发布时间排序，保留最新的
                sorted_news = sorted(news_list, key=lambda x: x.get('published_at', ''), reverse=True)
                
                # 删除除最新之外的所有新闻
                for news in sorted_news[1:]:
                    pg_service.delete_news_by_title(news['title'])
                    deleted_count += 1
        
        return {"message": f"Cleaned {deleted_count} duplicate news articles"}
        
    except Exception as e:
        print(f"Error cleaning duplicates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean duplicates: {str(e)}")

@router.post("/news/clean-duplicates-direct")
def clean_duplicate_news_direct(pg_service: PostgresService = Depends(get_pg_service)):
    """直接清理重复新闻（使用SQL）"""
    try:
        # 使用SQL直接删除重复的新闻
        deleted_count = pg_service.clean_duplicates_direct()
        return {"message": f"Cleaned {deleted_count} duplicate news articles"}
        
    except Exception as e:
        print(f"Error cleaning duplicates directly: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean duplicates: {str(e)}")

@router.post("/news/clean-old")
def clean_old_news(
    pg_service: PostgresService = Depends(get_pg_service),
    cutoff_date: str = Body(...),
    force: bool = Body(False)
):
    """清理旧新闻"""
    try:
        # 解析截止日期
        try:
            cutoff = datetime.fromisoformat(cutoff_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        # 获取要删除的新闻数量
        old_news_count = pg_service.get_old_news_count(cutoff)
        
        if old_news_count == 0:
            return {"message": "No old news to clean"}
        
        if not force:
            return {
                "message": f"Found {old_news_count} old news articles to clean",
                "cutoff_date": cutoff_date,
                "count": old_news_count,
                "force_required": True
            }
        
        # 执行删除
        deleted_count = pg_service.clean_old_news(cutoff)
        return {"message": f"Cleaned {deleted_count} old news articles"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error cleaning old news: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean old news: {str(e)}")