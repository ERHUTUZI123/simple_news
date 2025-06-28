#!/usr/bin/env python3
"""
简单测试RSS获取功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news.fetch_news import get_tech_news
from datetime import datetime

def test_rss_only():
    """只测试RSS获取功能"""
    print("🔍 测试RSS获取功能...")
    print(f"⏰ 当前时间: {datetime.utcnow()}")
    
    try:
        # 获取RSS新闻
        news_items = get_tech_news(force_refresh=True)
        print(f"✅ 从RSS获取到 {len(news_items)} 条新闻")
        
        if not news_items:
            print("❌ 没有获取到新闻")
            return
        
        # 显示最新的10条新闻
        print("\n📊 最新10条RSS新闻:")
        for i, item in enumerate(news_items[:10]):
            print(f"{i+1}. {item['title'][:60]}...")
            print(f"   来源: {item['source']}")
            print(f"   时间: {item['date']}")
            print()
        
        # 检查时间分布
        print("📈 时间分布分析:")
        recent_count = 0
        for item in news_items:
            try:
                date_str = item['date']
                if 'T' in date_str:
                    # 解析ISO格式时间
                    if date_str.endswith('Z'):
                        date_str = date_str[:-1] + '+00:00'
                    parsed_date = datetime.fromisoformat(date_str)
                    now = datetime.utcnow()
                    time_diff = now - parsed_date.replace(tzinfo=None)
                    hours_diff = time_diff.total_seconds() / 3600
                    
                    if hours_diff <= 24:
                        recent_count += 1
            except Exception as e:
                print(f"⚠️ 无法解析时间: {item['date']} - {e}")
        
        print(f"📊 24小时内的新闻: {recent_count}/{len(news_items)}")
        
    except Exception as e:
        print(f"❌ RSS获取异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rss_only() 