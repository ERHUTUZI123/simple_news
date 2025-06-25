#!/usr/bin/env python3
"""
测试速率限制处理功能
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_rate_limit_handling():
    """测试速率限制处理"""
    print("🧪 测试速率限制处理...")
    
    # 测试文本
    test_text = """
    Apple Inc. today announced the iPhone 15 Pro and iPhone 15 Pro Max, 
    featuring the most advanced Pro camera system ever, the A17 Pro chip 
    for next-level performance and mobile gaming, and a strong and light 
    titanium design. The new iPhone 15 Pro models introduce a new level 
    of performance and capabilities, making them the most powerful and 
    advanced Pro lineup ever.
    """
    
    # 测试摘要生成
    print("📝 测试摘要生成...")
    try:
        response = requests.post(
            f"{BASE_URL}/news/summary",
            json={"content": test_text},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 摘要生成成功: {result['summary'][:100]}...")
        else:
            print(f"❌ 摘要生成失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 摘要生成异常: {e}")
    
    # 测试评分
    print("🎯 测试AI评分...")
    try:
        response = requests.get(
            f"{BASE_URL}/news/score",
            params={"text": test_text},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI评分成功: {result['ai_score']}")
        else:
            print(f"❌ AI评分失败: {response.status_code}")
    except Exception as e:
        print(f"❌ AI评分异常: {e}")
    
    # 测试新闻列表（包含AI评分）
    print("📰 测试新闻列表...")
    try:
        response = requests.get(
            f"{BASE_URL}/news/today",
            params={"limit": 5, "sort_by": "ai_quality"},
            timeout=30
        )
        if response.status_code == 200:
            results = response.json()
            print(f"✅ 获取到 {len(results)} 条新闻")
            for i, news in enumerate(results[:3]):
                print(f"  {i+1}. {news['title'][:50]}... (AI评分: {news['ai_score']})")
        else:
            print(f"❌ 新闻列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 新闻列表异常: {e}")

if __name__ == "__main__":
    test_rate_limit_handling() 