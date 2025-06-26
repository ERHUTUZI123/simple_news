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
from app.models import SavedArticle, User, News
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID

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
    sort_by: str = Query("smart"),  # 默认使用智能排序
    source_filter: str = Query(None)
):
    """获取今日新闻，支持智能排序"""
    # 获取 Postgres 的新闻
    news_items = pg_service.get_news(offset, limit, sort_by, source_filter)
    
    # 检查是否需要刷新新闻
    should_refresh = False
    if not news_items:
        should_refresh = True
    else:
        # 检查最新新闻的年龄，如果超过2小时就刷新
        latest_news = pg_service.get_news(0, 1, "time")
        if latest_news and len(latest_news) > 0:
            latest_date_str = latest_news[0].get('published_at')
            if latest_date_str:
                try:
                    latest_date = datetime.fromisoformat(latest_date_str.replace('Z', '+00:00'))
                    now = datetime.utcnow()
                    if (now - latest_date) > timedelta(hours=2):
                        should_refresh = True
                except:
                    should_refresh = True
    
    if should_refresh:
        # 抓取 RSS 并存入
        raw = get_tech_news(force_refresh=True)
        pg_service.save_news(raw)
        news_items = pg_service.get_news(offset, limit, sort_by, source_filter)
    
    return news_items

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
        raw = get_tech_news(force_refresh=True)
        success = pg_service.save_news(raw)
        if success:
            return {"message": "News refreshed successfully", "count": len(raw)}
        else:
            raise HTTPException(status_code=500, detail="Failed to save news")
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
    """获取排序选项"""
    return {
        "options": [
            {"value": "smart", "label": "Smart Sort (Recommended)"},
            {"value": "time", "label": "Latest First"},
            {"value": "headlines", "label": "Most Popular"}
        ]
    }

@router.post("/api/save")
async def save_article(request: Request, pg_service: PostgresService = Depends(get_pg_service)):
    """保存文章到用户收藏"""
    try:
        data = await request.json()
        user_id = UUID(data.get("userId"))
        news_id = UUID(data.get("newsId"))
        
        if not user_id or not news_id:
            raise HTTPException(status_code=400, detail="Missing userId or newsId")
        
        # 检查文章是否存在
        article = pg_service.get_article_by_title(news_id)
        if "error" in article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # 保存到数据库
        success = pg_service.save_article_for_user(user_id, news_id)
        if success:
            return {"success": True, "message": "Article saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save article")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving article: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/api/save")
async def unsave_article(request: Request, pg_service: PostgresService = Depends(get_pg_service)):
    """从用户收藏中移除文章"""
    try:
        data = await request.json()
        user_id = UUID(data.get("userId"))
        news_id = UUID(data.get("newsId"))
        
        if not user_id or not news_id:
            raise HTTPException(status_code=400, detail="Missing userId or newsId")
        
        # 从数据库中移除
        success = pg_service.remove_article_from_user(user_id, news_id)
        if success:
            return {"success": True, "message": "Article removed from saved"}
        else:
            raise HTTPException(status_code=500, detail="Failed to remove article")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error removing article: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/saved")
async def get_saved_articles(
    user_id: str = Query(...),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """获取用户保存的文章列表"""
    try:
        user_id = UUID(user_id)
        saved_articles = pg_service.get_saved_articles_for_user(user_id)
        return {"articles": saved_articles}
    except Exception as e:
        print(f"Error getting saved articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/saved/check")
async def check_article_saved(
    user_id: str = Query(...),
    news_id: str = Query(...),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """检查文章是否已被用户保存"""
    try:
        user_id = UUID(user_id)
        news_id = UUID(news_id)
        is_saved = pg_service.is_article_saved_by_user(user_id, news_id)
        return {"saved": is_saved}
    except Exception as e:
        print(f"Error checking saved status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/auth/save-user")
async def save_user(request: Request, pg_service: PostgresService = Depends(get_pg_service)):
    """保存Google用户信息到数据库"""
    try:
        data = await request.json()
        user_id = data.get("id")
        email = data.get("email")
        name = data.get("name")
        
        if not user_id or not email:
            raise HTTPException(status_code=400, detail="Missing required user information")
        
        # 保存用户到数据库
        success = pg_service.save_user(user_id, email, name)
        if success:
            return {"success": True, "message": "User saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save user")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/news/clean-duplicates")
def clean_duplicate_news(pg_service: PostgresService = Depends(get_pg_service)):
    """清理重复的新闻条目"""
    try:
        # 获取所有新闻
        all_news = pg_service.db.query(News).all()
        print(f"🔍 Found {len(all_news)} total news articles")
        
        # 按标准化标题分组
        title_groups = {}
        for news in all_news:
            normalized_title = pg_service._normalize_title(news.title)
            if normalized_title not in title_groups:
                title_groups[normalized_title] = []
            title_groups[normalized_title].append(news)
        
        # 找出重复的组
        duplicates_removed = 0
        for normalized_title, news_list in title_groups.items():
            if len(news_list) > 1:
                print(f"🔍 Found {len(news_list)} duplicates for: {normalized_title[:50]}...")
                
                # 保留最新的一个，删除其他的
                sorted_news = sorted(news_list, key=lambda x: x.created_at, reverse=True)
                for news_to_delete in sorted_news[1:]:
                    pg_service.db.delete(news_to_delete)
                    duplicates_removed += 1
                    print(f"🗑️ Deleted duplicate: {news_to_delete.title[:50]}...")
        
        pg_service.db.commit()
        print(f"✅ Cleaned up {duplicates_removed} duplicate articles")
        
        return {
            "success": True, 
            "message": f"Cleaned up {duplicates_removed} duplicate articles",
            "duplicates_removed": duplicates_removed
        }
        
    except Exception as e:
        print(f"❌ Error cleaning duplicates: {e}")
        pg_service.db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clean duplicates: {str(e)}")