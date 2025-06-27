#!/usr/bin/env python3
"""
手动刷新生产环境新闻
"""

import requests
import json
from datetime import datetime

# 生产环境API地址
PRODUCTION_API = "https://simplenews-production.up.railway.app"

def check_current_news():
    """检查当前新闻状态"""
    try:
        print("🔍 检查当前新闻状态...")
        response = requests.get(f"{PRODUCTION_API}/news/today?limit=5")
        
        if response.status_code == 200:
            news_list = response.json()
            print(f"📰 当前有 {len(news_list)} 条新闻")
            
            if news_list:
                latest_news = news_list[0]
                print(f"📅 最新新闻: {latest_news.get('title', 'N/A')[:50]}...")
                print(f"⏰ 发布时间: {latest_news.get('published_at', 'N/A')}")
                print(f"📊 来源: {latest_news.get('source', 'N/A')}")
            else:
                print("❌ 没有新闻数据")
        else:
            print(f"❌ 检查失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查异常: {e}")

def refresh_news():
    """手动刷新新闻"""
    try:
        print("\n🔄 开始手动刷新新闻...")
        response = requests.post(f"{PRODUCTION_API}/news/refresh")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 刷新成功: {result.get('message', 'N/A')}")
            print(f"📊 获取到 {result.get('count', 0)} 条新闻")
        else:
            print(f"❌ 刷新失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 刷新异常: {e}")

def main():
    print("=" * 60)
    print("🔄 生产环境新闻刷新工具")
    print("=" * 60)
    
    # 检查当前状态
    check_current_news()
    
    # 询问是否刷新
    print("\n" + "-" * 60)
    user_input = input("是否要手动刷新新闻? (y/N): ").strip().lower()
    
    if user_input in ['y', 'yes']:
        refresh_news()
        
        # 刷新后再次检查
        print("\n" + "-" * 60)
        print("🔄 刷新后检查状态...")
        check_current_news()
    else:
        print("❌ 取消刷新")

if __name__ == "__main__":
    main() 