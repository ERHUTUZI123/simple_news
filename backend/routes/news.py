# --- Summarization & Scoring Endpoints (LLM Agent) ---
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.model_inference import summarize_article, batch_summarize, importance_score

router = APIRouter()

class ArticleRequest(BaseModel):
    article: str

class BatchRequest(BaseModel):
    articles: List[str]

class SummaryResponse(BaseModel):
    summary: str
    score: float

class BatchSummaryResponse(BaseModel):
    summaries: List[str]
    scores: List[float]

@router.post("/summarize", response_model=SummaryResponse)
def summarize(req: ArticleRequest):
    try:
        summary = summarize_article(req.article)
        score = importance_score(req.article, summary)
        return {"summary": summary, "score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch_summarize", response_model=BatchSummaryResponse)
def batch(req: BatchRequest):
    try:
        summaries = batch_summarize(req.articles)
        scores = [importance_score(a, s) for a, s in zip(req.articles, summaries)]
        return {"summaries": summaries, "scores": scores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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

# Rate limit configuration
RATE_LIMIT_DELAY = 2.0  # Base delay time (seconds)
MAX_RETRIES = 3  # Maximum retry attempts

def handle_openai_rate_limit(func):
    """Decorator: Handle OpenAI rate limiting"""
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e)
                if "rate_limit" in error_str.lower() or "429" in error_str:
                    if attempt < MAX_RETRIES - 1:
                        # Calculate delay time: base delay + random jitter
                        delay = RATE_LIMIT_DELAY + random.uniform(0, 1)
                        print(f"⚠️ [RATE_LIMIT] Attempt {attempt + 1} failed, retrying in {delay:.2f}s...")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"❌ [RATE_LIMIT] Max retries reached, returning default value")
                        return None
                else:
                    # Non-rate limit error, raise directly
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
    """Get the first n words of text"""
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
    Get news list, sorted by time (newest first)
    """
    try:
        # Use PostgresService to get news, sorted by time
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
    """Vote endpoint"""
    new_count = pg_service.update_vote(title, delta)
    return {"count": new_count}

@router.get("/news/vote")
def get_vote(
    title: str = Query(...),
    pg_service: PostgresService = Depends(get_pg_service)
):
    """Get vote count"""
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
    """Get article by title"""
    return pg_service.get_article_by_title(title)

@router.get("/news/article/{article_id}")
def get_article_by_id(article_id: str):
    """Get article by ID (compatibility endpoint)"""
    # Specific logic can be implemented here as needed
    return {"error": "Article not found"}

@router.post("/news/refresh")
def refresh_news(
    pg_service: PostgresService = Depends(get_pg_service)
):
    """Manually refresh news"""
    try:
        # Fetch RSS and save
        raw = get_tech_news(force_refresh=True)
        pg_service.save_news(raw)
        return {"message": "News refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh news: {str(e)}")

@router.get("/news/sources")
def get_news_sources(
    pg_service: PostgresService = Depends(get_pg_service)
):
    """Get all news sources"""
    try:
        # Return all supported news sources
        sources = [
            # American mainstream media
            "The New York Times", "The Washington Post", "Los Angeles Times", 
            "NBC News", "CBS News", "ABC News", "Fox News", "CNBC", "Axios",
            # International news agencies
            "Reuters", "Associated Press", "Bloomberg",
            # British media
            "BBC News", "The Guardian", "The Telegraph", 
            "Financial Times", "Sky News", "The Independent",
            # European media
            "Euronews", "Deutsche Welle",
            # Middle Eastern media
            "Al Jazeera",
        ]
        return {"sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sources: {str(e)}")

@router.get("/news/sort-options")
def get_sort_options():
    """Get sort options (deprecated, kept for compatibility)"""
    return {
        "sort_options": [
            {"value": "time", "label": "Latest First"}
        ]
    }

@router.post("/api/save")
async def save_article(request: Request, pg_service: PostgresService = Depends(get_pg_service)):
    """Save article"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        news_id = data.get("news_id")
        
        if not user_id or not news_id:
            raise HTTPException(status_code=400, detail="Missing user_id or news_id")
        
        # Check if user exists, create if not
        user = pg_service.get_user_by_id(user_id)
        if not user:
            user_data = data.get("user", {})
            user = pg_service.create_user(user_id, user_data.get("email"), user_data.get("name"))
        
        # Save article
        saved_article = pg_service.save_article(user_id, news_id)
        return {"message": "Article saved successfully", "saved_article": saved_article}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving article: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/api/save")
async def unsave_article(request: Request, pg_service: PostgresService = Depends(get_pg_service)):
    """Unsave article"""
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
    """Get user's saved articles"""
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
    """Check if article is saved"""
    try:
        is_saved = pg_service.is_article_saved(user_id, news_id)
        return {"is_saved": is_saved}
        
    except Exception as e:
        print(f"Error checking saved article: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/auth/save-user")
async def save_user(request: Request, pg_service: PostgresService = Depends(get_pg_service)):
    """Save user information"""
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
    """Clean duplicate news"""
    try:
        # Get all news
        all_news = pg_service.get_all_news()
        
        # Group by title, find duplicates
        title_groups = {}
        for news in all_news:
            title = news.get('title', '').strip().lower()
            if title:
                if title not in title_groups:
                    title_groups[title] = []
                title_groups[title].append(news)
        
        # Delete duplicate news (keep newest)
        deleted_count = 0
        for title, news_list in title_groups.items():
            if len(news_list) > 1:
                # Sort by publish time, keep newest
                sorted_news = sorted(news_list, key=lambda x: x.get('published_at', ''), reverse=True)
                
                # Delete all news except the newest
                for news in sorted_news[1:]:
                    pg_service.delete_news_by_title(news['title'])
                    deleted_count += 1
        
        return {"message": f"Cleaned {deleted_count} duplicate news articles"}
        
    except Exception as e:
        print(f"Error cleaning duplicates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean duplicates: {str(e)}")

@router.post("/news/clean-duplicates-direct")
def clean_duplicate_news_direct(pg_service: PostgresService = Depends(get_pg_service)):
    """Directly clean duplicate news (using SQL)"""
    try:
        # Use SQL to directly delete duplicate news
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
    """Clean old news"""
    try:
        # Parse cutoff date
        try:
            cutoff = datetime.fromisoformat(cutoff_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        # Get count of news to delete
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
        
        # Execute deletion
        deleted_count = pg_service.clean_old_news(cutoff)
        return {"message": f"Cleaned {deleted_count} old news articles"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error cleaning old news: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean old news: {str(e)}")