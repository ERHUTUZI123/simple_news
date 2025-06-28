#!/usr/bin/env python3
"""
强制刷新新闻脚本
"""

import requests
import json
import time
from datetime import datetime

# 生产环境API地址
PRODUCTION_API = "https://simplenews-production.up.railway.app"

def force_refresh_news():
    """强制刷新新闻"""
    print("🔄 开始强制刷新新闻...")
    
    try:
        # 多次尝试刷新
        for attempt in range(3):
            print(f"🔄 第 {attempt + 1} 次尝试刷新...")
            
            # 尝试刷新新闻
            response = requests.post(f"{PRODUCTION_API}/news/refresh", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 刷新成功: {result.get('message', 'N/A')}")
                print(f"📊 获取到 {result.get('count', 0)} 条新闻")
                break
            else:
                print(f"❌ 刷新失败: {response.status_code} - {response.text}")
                
            # 等待一下再重试
            if attempt < 2:
                time.sleep(5)
                
    except Exception as e:
        print(f"❌ 刷新异常: {e}")

def check_latest_news():
    """检查最新新闻"""
    try:
        print("\n📰 检查最新新闻...")
        response = requests.get(f"{PRODUCTION_API}/news/today?limit=5", timeout=10)
        
        if response.status_code == 200:
            news_list = response.json()
            print(f"📊 当前有 {len(news_list)} 条新闻")
            
            if news_list:
                latest_news = news_list[0]
                print(f"📅 最新新闻: {latest_news.get('title', 'N/A')[:60]}...")
                print(f"⏰ 发布时间: {latest_news.get('published_at', 'N/A')}")
                print(f"📊 来源: {latest_news.get('source', 'N/A')}")
                
                # 检查时间差
                try:
                    latest_date_str = latest_news.get('published_at', '')
                    if latest_date_str:
                        latest_date = datetime.fromisoformat(latest_date_str.replace('Z', '+00:00'))
                        now = datetime.utcnow()
                        time_diff = now - latest_date.replace(tzinfo=None)
                        hours_diff = time_diff.total_seconds() / 3600
                        print(f"⏱️ 时间差: {hours_diff:.1f} 小时")
                        
                        if hours_diff > 24:
                            print("⚠️ 警告: 最新新闻超过24小时!")
                        else:
                            print("✅ 新闻时间正常")
                except Exception as e:
                    print(f"⚠️ 无法解析时间: {e}")
            else:
                print("❌ 没有新闻数据")
        else:
            print(f"❌ 检查失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查异常: {e}")

if __name__ == "__main__":
    print("🚀 开始强制刷新新闻流程...")
    print(f"⏰ 当前时间: {datetime.utcnow()}")
    
    # 检查当前状态
    check_latest_news()
    
    # 强制刷新
    force_refresh_news()
    
    # 再次检查
    print("\n" + "="*50)
    time.sleep(10)  # 等待一下让刷新完成
    check_latest_news()
    
    print("\n✅ 强制刷新流程完成") 