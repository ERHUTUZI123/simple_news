"""
api.py

FastAPI app exposing endpoints for summarization and importance scoring.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from .model_inference import summarize_article, batch_summarize, importance_score

app = FastAPI(title="News Summarization & Scoring API")

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

@app.post("/summarize", response_model=SummaryResponse)
def summarize(req: ArticleRequest):
    try:
        summary = summarize_article(req.article)
        score = importance_score(req.article, summary)
        return {"summary": summary, "score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_summarize", response_model=BatchSummaryResponse)
def batch(req: BatchRequest):
    try:
        summaries = batch_summarize(req.articles)
        scores = [importance_score(a, s) for a, s in zip(req.articles, summaries)]
        return {"summaries": summaries, "scores": scores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
