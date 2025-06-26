#!/usr/bin/env python3
"""
测试智能排序功能
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scoring import (
    time_decay_weight, 
    ai_structure_score, 
    source_weight, 
    keyword_novelty_score, 
    headline_count_score,
    calculate_news_score,
    extract_keywords_from_text
)

load_dotenv()

def test_scoring_functions():
    """测试各个评分函数"""
    print("🧪 Testing scoring functions...")
    
    # 测试时间衰减
    now = datetime.utcnow()
    recent_time = now - timedelta(hours=2)
    old_time = now - timedelta(hours=24)
    
    print(f"⏰ Time decay (2h ago): {time_decay_weight(recent_time):.3f}")
    print(f"⏰ Time decay (24h ago): {time_decay_weight(old_time):.3f}")
    
    # 测试AI结构评分
    summary_ai_good = {"structure_score": 4.5}
    summary_ai_bad = {"structure_score": 1.5}
    
    print(f"🧠 AI score (good): {ai_structure_score(summary_ai_good):.3f}")
    print(f"🧠 AI score (bad): {ai_structure_score(summary_ai_bad):.3f}")
    
    # 测试来源权重
    print(f"🗞️ Source weight (Financial Times): {source_weight('Financial Times'):.3f}")
    print(f"🗞️ Source weight (Unknown): {source_weight('Unknown Source'):.3f}")
    
    # 测试关键词新颖度
    existing_keywords = {"ai": 3, "tech": 2, "news": 1}
    new_keywords = ["ai", "blockchain", "crypto"]
    old_keywords = ["ai", "tech", "news"]
    
    print(f"🔍 Novelty score (new): {keyword_novelty_score(new_keywords, existing_keywords):.3f}")
    print(f"🔍 Novelty score (old): {keyword_novelty_score(old_keywords, existing_keywords):.3f}")
    
    # 测试点赞数评分
    print(f"⭐ Headline score (5): {headline_count_score(5):.3f}")
    print(f"⭐ Headline score (25): {headline_count_score(25):.3f}")
    
    # 测试综合评分
    score = calculate_news_score(
        published_at=recent_time,
        summary_ai=summary_ai_good,
        source="Financial Times",
        keywords=new_keywords,
        headline_count=10,
        existing_keyword_map=existing_keywords
    )
    
    print(f"📊 Total score: {score:.3f}")
    
    # 测试关键词提取
    text = "Artificial Intelligence is transforming the technology industry with new breakthroughs in machine learning and deep neural networks."
    keywords = extract_keywords_from_text(text)
    print(f"🏷️ Extracted keywords: {keywords}")

def test_news_scenarios():
    """测试不同新闻场景的评分"""
    print("\n📰 Testing different news scenarios...")
    
    now = datetime.utcnow()
    existing_keywords = {"ai": 5, "tech": 3, "news": 2, "business": 1}
    
    scenarios = [
        {
            "name": "Recent High-Quality News",
            "published_at": now - timedelta(hours=1),
            "summary_ai": {"structure_score": 4.5},
            "source": "Financial Times",
            "keywords": ["blockchain", "crypto", "finance"],
            "headline_count": 15
        },
        {
            "name": "Old Low-Quality News",
            "published_at": now - timedelta(hours=48),
            "summary_ai": {"structure_score": 2.0},
            "source": "Unknown Source",
            "keywords": ["ai", "tech", "news"],
            "headline_count": 2
        },
        {
            "name": "Medium Quality Recent News",
            "published_at": now - timedelta(hours=6),
            "summary_ai": {"structure_score": 3.5},
            "source": "Reuters",
            "keywords": ["climate", "environment", "policy"],
            "headline_count": 8
        }
    ]
    
    for scenario in scenarios:
        score = calculate_news_score(
            published_at=scenario["published_at"],
            summary_ai=scenario["summary_ai"],
            source=scenario["source"],
            keywords=scenario["keywords"],
            headline_count=scenario["headline_count"],
            existing_keyword_map=existing_keywords
        )
        
        print(f"📊 {scenario['name']}: {score:.3f}")

if __name__ == "__main__":
    test_scoring_functions()
    test_news_scenarios()
    print("\n✅ All tests completed!") 