#!/usr/bin/env python3
"""
清理数据库中的错误日期数据
"""

import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    sys.exit(1)

def clean_database_dates():
    """清理数据库中的错误日期数据"""
    try:
        # 创建数据库引擎
        engine = create_engine(DATABASE_URL)  # type: ignore
        
        with engine.connect() as conn:
            print("🧹 Starting database date cleanup...")
            
            # 查找错误的日期（未来日期或无效日期）
            now = datetime.utcnow()
            future_threshold = now + timedelta(hours=1)  # 1小时后的日期被认为是错误的
            
            # 查找未来日期的新闻
            result = conn.execute(text("""
                SELECT id, title, published_at, date 
                FROM news 
                WHERE published_at > :future_threshold
                ORDER BY published_at DESC
            """), {"future_threshold": future_threshold})
            
            future_news = result.fetchall()
            print(f"📅 Found {len(future_news)} news items with future dates")
            
            if future_news:
                print("\n🔍 Future dates found:")
                for row in future_news:
                    print(f"  ID: {row[0]}, Title: {row[1][:50]}..., Date: {row[2]}")
                
                # 更新这些新闻的日期为当前时间
                update_result = conn.execute(text("""
                    UPDATE news 
                    SET published_at = :now, date = :now
                    WHERE published_at > :future_threshold
                """), {
                    "now": now,
                    "future_threshold": future_threshold
                })
                
                print(f"✅ Updated {update_result.rowcount} news items with current time")
            
            # 查找空日期的新闻
            result = conn.execute(text("""
                SELECT id, title, published_at, date 
                FROM news 
                WHERE published_at IS NULL OR date IS NULL
            """))
            
            null_news = result.fetchall()
            print(f"📅 Found {len(null_news)} news items with null dates")
            
            if null_news:
                print("\n🔍 Null dates found:")
                for row in null_news:
                    print(f"  ID: {row[0]}, Title: {row[1][:50]}...")
                
                # 更新这些新闻的日期为当前时间
                update_result = conn.execute(text("""
                    UPDATE news 
                    SET published_at = :now, date = :now
                    WHERE published_at IS NULL OR date IS NULL
                """), {"now": now})
                
                print(f"✅ Updated {update_result.rowcount} news items with current time")
            
            conn.commit()
            print("✅ Database date cleanup completed!")
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_database_dates() 