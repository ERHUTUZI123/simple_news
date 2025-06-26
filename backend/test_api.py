#!/usr/bin/env python3
"""
测试API返回的日期格式
"""

import requests
import json

def test_api_dates():
    """测试API返回的日期格式"""
    try:
        # 测试新闻API
        response = requests.get("https://simplenews-production.up.railway.app/news/today?limit=3")
        
        if response.status_code == 200:
            news_data = response.json()
            print("✅ API响应成功")
            print(f"📰 获取到 {len(news_data)} 条新闻")
            
            for i, news in enumerate(news_data):
                print(f"\n--- 新闻 {i+1} ---")
                print(f"标题: {news.get('title', 'N/A')[:50]}...")
                print(f"日期字段: {news.get('date', 'N/A')}")
                print(f"发布时间: {news.get('published_at', 'N/A')}")
                print(f"来源: {news.get('source', 'N/A')}")
                
                # 检查日期格式
                date_str = news.get('date')
                if date_str:
                    print(f"日期类型: {type(date_str)}")
                    print(f"日期长度: {len(date_str)}")
                    print(f"日期内容: '{date_str}'")
                else:
                    print("❌ 日期字段为空")
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_api_dates() 