"""
api.py

FastAPI application exposing production-ready endpoints for news summarization and importance scoring.
Designed for high-throughput processing of ~30,000 articles per day with structured outputs for 
downstream decision-making and research dashboards.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .model_inference import (
    summarize_article,
    batch_summarize,
    importance_score,
    process_article_batch
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="News Summarization & Rating AI Agent API",
    description="Scalable news summarization and rating system using 7B-parameter instruction-tuned LLM",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models with structured schemas
class ArticleRequest(BaseModel):
    article: str = Field(..., description="News article text to summarize", min_length=50)
    use_cache: bool = Field(True, description="Whether to use cached results")

class BatchRequest(BaseModel):
    articles: List[str] = Field(..., description="List of article texts", min_items=1, max_items=100)
    batch_size: Optional[int] = Field(None, description="Custom batch size for processing")

class SummaryResponse(BaseModel):
    """Structured response for single article summarization"""
    summary: str = Field(..., description="Generated summary")
    score: float = Field(..., description="Importance score (0.0-1.0)", ge=0.0, le=1.0)
    timestamp: str = Field(..., description="Processing timestamp (ISO format)")
    article_length: int = Field(..., description="Original article character count")
    summary_length: int = Field(..., description="Generated summary character count")
    model_version: str = Field("7b-instruction-tuned", description="Model version used")

class BatchSummaryResponse(BaseModel):
    """Structured response for batch processing"""
    results: List[SummaryResponse] = Field(..., description="List of summarization results")
    total_processed: int = Field(..., description="Total articles processed")
    processing_time_ms: Optional[float] = Field(None, description="Total processing time in milliseconds")
    batch_size: int = Field(..., description="Batch size used for processing")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    cache_size: int
    timestamp: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    from .model_inference import _model_loaded, summary_cache
    return {
        "status": "healthy",
        "model_loaded": _model_loaded,
        "cache_size": len(summary_cache) if summary_cache else 0,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/summarize", response_model=SummaryResponse)
async def summarize(req: ArticleRequest):
    """
    Summarize a single news article and calculate importance score.
    
    Returns structured output suitable for downstream integration.
    """
    try:
        start_time = datetime.utcnow()
        
        summary = summarize_article(req.article, use_cache=req.use_cache)
        score = importance_score(req.article, summary)
        
        return SummaryResponse(
            summary=summary,
            score=score,
            timestamp=datetime.utcnow().isoformat(),
            article_length=len(req.article),
            summary_length=len(summary),
            model_version="7b-instruction-tuned"
        )
    except Exception as e:
        logger.error(f"Error in summarize endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_summarize", response_model=BatchSummaryResponse)
async def batch_summarize_endpoint(req: BatchRequest, background_tasks: BackgroundTasks):
    """
    Batch summarization endpoint optimized for high-throughput processing.
    
    Processes multiple articles efficiently using batching and caching.
    Designed to handle large volumes (e.g., 30K articles/day) with low latency.
    """
    import time
    start_time = time.time()
    
    try:
        # Process batch with optimized batching
        results = process_article_batch(req.articles)
        
        # Convert to response format
        summary_responses = [
            SummaryResponse(
                summary=r["summary"],
                score=r["score"],
                timestamp=r["timestamp"],
                article_length=r["article_length"],
                summary_length=r["summary_length"],
                model_version="7b-instruction-tuned"
            )
            for r in results
        ]
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return BatchSummaryResponse(
            results=summary_responses,
            total_processed=len(results),
            processing_time_ms=processing_time,
            batch_size=req.batch_size or 8
        )
    except Exception as e:
        logger.error(f"Error in batch_summarize endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_stream")
async def process_stream(articles: List[str]):
    """
    Stream processing endpoint for continuous article ingestion.
    
    Optimized for real-time processing of articles as they arrive.
    Returns results as they are processed (streaming response).
    """
    from fastapi.responses import StreamingResponse
    import json
    
    async def generate():
        for article in articles:
            try:
                result = process_article_batch([article])[0]
                yield f"data: {json.dumps(result)}\n\n"
            except Exception as e:
                logger.error(f"Error processing article in stream: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/stats")
async def get_stats():
    """
    Get system statistics for monitoring and optimization.
    """
    from .model_inference import summary_cache, score_cache, _model_loaded
    
    return {
        "model_loaded": _model_loaded,
        "summary_cache_size": len(summary_cache) if summary_cache else 0,
        "score_cache_size": len(score_cache) if score_cache else 0,
        "cache_hit_rate": "N/A",  # Can be implemented with metrics
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "News Summarization & Rating AI Agent",
        "version": "1.0.0",
        "description": "Scalable news summarization system using 7B-parameter instruction-tuned LLM",
        "endpoints": {
            "/summarize": "Single article summarization",
            "/batch_summarize": "Batch processing for high throughput",
            "/process_stream": "Streaming processing endpoint",
            "/health": "Health check",
            "/stats": "System statistics"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
