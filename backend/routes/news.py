from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.news.fetch_news import get_tech_news
from app.news.db import SessionLocal
from backend.models import Vote
from urllib.parse import urlparse
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_first_n_words(text, n=600):
    return ' '.join(text.split()[:n])

@router.get("/news/today")
def get_today_news(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    raw = get_tech_news()
    results = []
    for item in raw:
        source = item.get("source") or urlparse(item["link"]).netloc.replace("www.", "")
        vote = db.query(Vote).filter(Vote.title == item["title"]).first()
        score = vote.count if vote else 0

        content = item.get("content") or item.get("summary") or ""
        summary = get_first_n_words(content, 600)

        results.append({
            "title":   item["title"],
            "content": content,
            "summary": summary,
            "link":    item["link"],
            "date":    item["date"],
            "source":  source,
            "score":   score
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[offset:offset+limit]

@router.post("/news/vote")
def vote_news(
    title: str = Query(...),
    delta: int = Query(1),
    db: Session = Depends(get_db)
):
    vote = db.query(Vote).filter(Vote.title == title).first()
    if vote:
        vote.count += delta
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
    return {"summary": summarize_news(text, 300)}

@router.get("/news/score")
def news_score(text: str = Query(...)):
    # 独立打分接口，返回 1-10 分
    score = score_news(text)
    return {"ai_score": score}


def summarize_news(text: str, word_count: int = 70) -> str:
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
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI summarize error:", e)
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
    "J"
        f"{text}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.2,
        )
        score_str = resp.choices[0].message.content.strip()
        score = int(''.join(filter(str.isdigit, score_str)))
        return max(1, min(score, 10))
    except Exception as e:
        print("OpenAI score error:", e)
        return None