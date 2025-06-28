#!/usr/bin/env python3
"""
测试新闻刷新和去重逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.news.postgres_service import PostgresService
from news.fetch_news import get_tech_news
from datetime import datetime

def test_news_refresh():
    """测试新闻刷新"""
    print("🔍 测试新闻刷新和去重逻辑...")
    
    # 获取新新闻
    print("📰 获取RSS新闻...")
    news_items = get_tech_news(force_refresh=True)
    print(f"✅ 从RSS获取到 {len(news_items)} 条新闻")
    
    if not news_items:
        print("❌ 没有获取到新闻")
        return
    
    # 显示最新的5条新闻
    print("\n📊 最新5条RSS新闻:")
    for i, item in enumerate(news_items[:5]):
        print(f"{i+1}. {item['title'][:60]}...")
        print(f"   来源: {item['source']}")
        print(f"   时间: {item['date']}")
        print()
    
    # 测试数据库保存
    print("💾 测试数据库保存...")
    db = SessionLocal()
    try:
        pg_service = PostgresService(db)
        
        # 检查现有新闻数量
        existing_news = pg_service.get_news(0, 1000, "time")
        print(f"📊 数据库中现有 {len(existing_news)} 条新闻")
        
        # 测试去重逻辑
        print("\n🔍 测试去重逻辑:")
        for i, item in enumerate(news_items[:10]):
            is_duplicate = pg_service._is_duplicate_title(item['title'])
            status = "❌ 重复" if is_duplicate else "✅ 新文章"
            print(f"{i+1}. {status} - {item['title'][:50]}...")
        
        # 尝试保存新闻
        print(f"\n💾 尝试保存 {len(news_items)} 条新闻...")
        success = pg_service.save_news(news_items)
        
        if success:
            print("✅ 新闻保存成功")
            
            # 检查保存后的新闻
            updated_news = pg_service.get_news(0, 1000, "time")
            print(f"📊 保存后数据库中有 {len(updated_news)} 条新闻")
            
            if updated_news:
                latest = updated_news[0]
                print(f"📅 最新新闻: {latest.get('title', 'N/A')[:50]}...")
                print(f"⏰ 发布时间: {latest.get('published_at', 'N/A')}")
        else:
            print("❌ 新闻保存失败")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_news_refresh() 