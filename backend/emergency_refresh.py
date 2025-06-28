#!/usr/bin/env python3
"""
紧急刷新新闻脚本 - 清理旧数据并强制获取最新新闻
"""

import requests
import json
import time
from datetime import datetime, timedelta

# 生产环境API地址
PRODUCTION_API = "https://simplenews-production.up.railway.app"

def emergency_refresh():
    """紧急刷新新闻"""
    print("🚨 开始紧急刷新新闻...")
    print(f"⏰ 当前时间: {datetime.utcnow()}")
    
    try:
        # 1. 首先尝试清理旧数据
        print("\n🧹 尝试清理旧数据...")
        try:
            # 清理超过48小时的旧新闻
            cutoff_date = (datetime.utcnow() - timedelta(hours=48)).isoformat()
            cleanup_data = {
                "cutoff_date": cutoff_date,
                "force": True
            }
            response = requests.post(f"{PRODUCTION_API}/news/clean-old", json=cleanup_data, timeout=30)
            if response.status_code == 200:
                print("✅ 旧数据清理成功")
            else:
                print(f"⚠️ 清理失败: {response.status_code}")
        except Exception as e:
            print(f"⚠️ 清理异常: {e}")
        
        # 2. 强制刷新新闻
        print("\n🔄 强制刷新新闻...")
        for attempt in range(5):  # 尝试5次
            print(f"🔄 第 {attempt + 1} 次尝试...")
            
            try:
                response = requests.post(f"{PRODUCTION_API}/news/refresh", timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 刷新成功: {result.get('message', 'N/A')}")
                    print(f"📊 获取到 {result.get('count', 0)} 条新闻")
                    break
                else:
                    print(f"❌ 刷新失败: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ 刷新异常: {e}")
            
            # 等待一下再重试
            if attempt < 4:
                time.sleep(10)
        
        # 3. 检查结果
        print("\n📰 检查刷新结果...")
        time.sleep(15)  # 等待处理完成
        
        response = requests.get(f"{PRODUCTION_API}/news/today?limit=10", timeout=10)
        if response.status_code == 200:
            news_list = response.json()
            print(f"📊 当前有 {len(news_list)} 条新闻")
            
            if news_list:
                latest_news = news_list[0]
                print(f"📅 最新新闻: {latest_news.get('title', 'N/A')[:60]}...")
                print(f"⏰ 发布时间: {latest_news.get('published_at', latest_news.get('date', 'N/A'))}")
                print(f"📊 来源: {latest_news.get('source', 'N/A')}")
                
                # 检查时间差
                try:
                    date_str = latest_news.get('published_at') or latest_news.get('date', '')
                    if date_str:
                        if date_str.endswith('Z'):
                            date_str = date_str[:-1] + '+00:00'
                        latest_date = datetime.fromisoformat(date_str)
                        now = datetime.utcnow()
                        time_diff = now - latest_date.replace(tzinfo=None)
                        hours_diff = time_diff.total_seconds() / 3600
                        print(f"⏱️ 时间差: {hours_diff:.1f} 小时")
                        
                        if hours_diff > 24:
                            print("⚠️ 警告: 最新新闻仍然超过24小时!")
                            print("🔧 建议检查数据库连接和权限")
                        else:
                            print("✅ 新闻时间正常")
                except Exception as e:
                    print(f"⚠️ 无法解析时间: {e}")
            else:
                print("❌ 没有新闻数据")
        else:
            print(f"❌ 检查失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 紧急刷新异常: {e}")

def check_rss_status():
    """检查RSS源状态"""
    print("\n📡 检查RSS源状态...")
    
    # 测试几个主要RSS源
    test_sources = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml",
        "https://feeds.bloomberg.com/politics/news.rss"
    ]
    
    for i, url in enumerate(test_sources):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ RSS源 {i+1} 正常")
            else:
                print(f"❌ RSS源 {i+1} 异常: {response.status_code}")
        except Exception as e:
            print(f"❌ RSS源 {i+1} 连接失败: {e}")

if __name__ == "__main__":
    print("🚨 紧急新闻刷新流程")
    print("=" * 50)
    
    # 检查RSS源状态
    check_rss_status()
    
    # 执行紧急刷新
    emergency_refresh()
    
    print("\n" + "=" * 50)
    print("✅ 紧急刷新流程完成")
    print("\n💡 如果问题仍然存在，请检查:")
    print("1. Railway应用日志")
    print("2. 数据库连接状态")
    print("3. 应用权限设置") 