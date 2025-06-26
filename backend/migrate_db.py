#!/usr/bin/env python3
"""
数据库迁移脚本：添加智能排序相关字段
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    sys.exit(1)

def migrate_database():
    """执行数据库迁移"""
    try:
        # 创建数据库引擎
        engine = create_engine(DATABASE_URL)  # type: ignore
        
        with engine.connect() as conn:
            print("🔧 Starting database migration...")
            
            # 检查新字段是否已存在
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'news' 
                AND column_name IN ('published_at', 'summary_ai', 'headline_count', 'keywords', 'score')
            """))
            
            existing_columns = [row[0] for row in result]
            print(f"📋 Existing columns: {existing_columns}")
            
            # 添加新字段
            migrations = [
                ("published_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ("summary_ai", "JSONB"),
                ("headline_count", "INTEGER DEFAULT 0"),
                ("keywords", "JSONB"),
                ("score", "FLOAT DEFAULT 0.0")
            ]
            
            for column_name, column_type in migrations:
                if column_name not in existing_columns:
                    print(f"➕ Adding column: {column_name}")
                    conn.execute(text(f"ALTER TABLE news ADD COLUMN {column_name} {column_type}"))
                    conn.commit()
                else:
                    print(f"✅ Column {column_name} already exists")
            
            # 更新现有数据的published_at字段
            print("🔄 Updating existing data...")
            conn.execute(text("""
                UPDATE news 
                SET published_at = date 
                WHERE published_at IS NULL
            """))
            
            # 初始化headline_count字段
            conn.execute(text("""
                UPDATE news 
                SET headline_count = 0 
                WHERE headline_count IS NULL
            """))
            
            # 初始化score字段
            conn.execute(text("""
                UPDATE news 
                SET score = 0.0 
                WHERE score IS NULL
            """))
            
            conn.commit()
            
            print("✅ Database migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database() 