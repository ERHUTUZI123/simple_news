#!/usr/bin/env python3
"""
Smart Sort V2 测试脚本
测试新的智能评分系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.smart_scoring import (
    compute_significance_score, compute_freshness_score, compute_source_weight_score,
    compute_popularity_score, compute_novelty_score, compute_summary_quality_score,
    compute_smart_score, get_score_breakdown
)
from datetime import datetime, timedelta
import json

def test_significance_scoring():
    """测试重要性评分"""
    print("🧠 测试重要性评分...")
    
    test_cases = [
        {
            "title": "War breaks out in Ukraine as Russia launches invasion",
            "content": "Major conflict erupts in Eastern Europe with global implications",
            "expected_high": True
        },
        {
            "title": "New iPhone 15 released with advanced features",
            "content": "Apple launches latest smartphone with improved camera and battery",
            "expected_high": False
        },
        {
            "title": "President announces new economic policy",
            "content": "Major policy changes affecting national economy",
            "expected_high": True
        }
    ]
    
    for i, case in enumerate(test_cases):
        score = compute_significance_score(case["title"], case["content"])
        print(f"  {i+1}. '{case['title'][:50]}...' -> {score:.1f}")
        if case["expected_high"] and score >= 8:
            print(f"     ✅ 高重要性评分正确")
        elif not case["expected_high"] and score <= 6:
            print(f"     ✅ 低重要性评分正确")
        else:
            print(f"     ⚠️ 评分可能需要调整")

def test_freshness_scoring():
    """测试时效性评分"""
    print("\n⏰ 测试时效性评分...")
    
    now = datetime.utcnow()
    test_cases = [
        {"hours_ago": 1, "expected": 10},
        {"hours_ago": 5, "expected": 7},
        {"hours_ago": 10, "expected": 5},
        {"hours_ago": 20, "expected": 3},
        {"hours_ago": 30, "expected": 1},
        {"hours_ago": 60, "expected": 0}
    ]
    
    for case in test_cases:
        published_at = now - timedelta(hours=case["hours_ago"])
        score = compute_freshness_score(published_at)
        print(f"  {case['hours_ago']}小时前 -> {score:.1f} (期望: {case['expected']})")
        if abs(score - case["expected"]) <= 1:
            print(f"     ✅ 时效性评分正确")
        else:
            print(f"     ⚠️ 评分可能需要调整")

def test_source_weight_scoring():
    """测试来源权重评分"""
    print("\n📰 测试来源权重评分...")
    
    test_sources = [
        "The New York Times",
        "BBC News", 
        "Bloomberg",
        "NBC News",
        "The Independent",
        "Unknown Source"
    ]
    
    for source in test_sources:
        score = compute_source_weight_score(source)
        print(f"  {source} -> {score:.1f}")

def test_popularity_scoring():
    """测试流行度评分"""
    print("\n🔥 测试流行度评分...")
    
    test_cases = [
        {"headline_count": 0, "duplicate_count": 0},
        {"headline_count": 3, "duplicate_count": 0},
        {"headline_count": 8, "duplicate_count": 0},
        {"headline_count": 15, "duplicate_count": 0},
        {"headline_count": 5, "duplicate_count": 2},
    ]
    
    for case in test_cases:
        score = compute_popularity_score(case["headline_count"], case["duplicate_count"])
        print(f"  点赞数: {case['headline_count']}, 重复数: {case['duplicate_count']} -> {score:.1f}")

def test_novelty_scoring():
    """测试新颖性评分"""
    print("\n🆕 测试新颖性评分...")
    
    existing_titles = [
        "Trump wins election in landslide victory",
        "New AI breakthrough changes everything",
        "Stock market reaches all-time high"
    ]
    
    test_titles = [
        "Trump wins election in landslide victory",  # 完全重复
        "Trump wins election with overwhelming support",  # 高度相似
        "Biden wins election in close race",  # 中等相似
        "New technology revolutionizes healthcare",  # 轻微相似
        "Penguins discovered in Antarctica",  # 完全独特
    ]
    
    for title in test_titles:
        score = compute_novelty_score(title, existing_titles)
        print(f"  '{title[:50]}...' -> {score:.1f}")

def test_summary_quality_scoring():
    """测试摘要质量评分"""
    print("\n📝 测试摘要质量评分...")
    
    test_cases = [
        {"structure_score": 9.5, "expected": 10},
        {"structure_score": 7.0, "expected": 8},
        {"structure_score": 5.5, "expected": 6},
        {"structure_score": 2.0, "expected": 3},
        {"structure_score": 0.0, "expected": 0}
    ]
    
    for case in test_cases:
        summary_ai = {"structure_score": case["structure_score"]}
        score = compute_summary_quality_score(summary_ai)
        print(f"  结构评分: {case['structure_score']} -> {score:.1f} (期望: {case['expected']})")

def test_integrated_scoring():
    """测试综合智能评分"""
    print("\n🎯 测试综合智能评分...")
    
    # 模拟现有新闻
    existing_news = [
        {"title": "Previous news about technology"},
        {"title": "Old political news"}
    ]
    
    # 测试文章
    test_articles = [
        {
            "title": "Major breakthrough in quantum computing",
            "content": "Scientists achieve quantum supremacy in breakthrough experiment",
            "source": "The New York Times",
            "published_at": datetime.utcnow() - timedelta(hours=2),
            "headline_count": 5,
            "summary_ai": {"structure_score": 8.5}
        },
        {
            "title": "Celebrity wedding photos released",
            "content": "Famous actor gets married in lavish ceremony",
            "source": "Entertainment Weekly",
            "published_at": datetime.utcnow() - timedelta(hours=1),
            "headline_count": 10,
            "summary_ai": {"structure_score": 6.0}
        }
    ]
    
    for i, article in enumerate(test_articles):
        smart_score = compute_smart_score(article, existing_news)
        breakdown = get_score_breakdown(article, existing_news)
        
        print(f"\n  文章 {i+1}: '{article['title'][:50]}...'")
        print(f"    综合智能评分: {smart_score:.2f}")
        print(f"    详细分解:")
        for dimension, score in breakdown.items():
            if dimension != 'smart_score':
                print(f"      {dimension}: {score:.2f}")

def main():
    """主测试函数"""
    print("🚀 Smart Sort V2 测试开始\n")
    
    test_significance_scoring()
    test_freshness_scoring()
    test_source_weight_scoring()
    test_popularity_scoring()
    test_novelty_scoring()
    test_summary_quality_scoring()
    test_integrated_scoring()
    
    print("\n✅ Smart Sort V2 测试完成！")
    print("\n📊 评分维度总结:")
    print("  - Significance (30%): 事件影响力")
    print("  - Freshness (20%): 时效性")
    print("  - Source Weight (15%): 来源可信度")
    print("  - Popularity (10%): 流行度")
    print("  - Novelty (15%): 新颖性")
    print("  - Summary Quality (10%): 摘要质量")

if __name__ == "__main__":
    main() 