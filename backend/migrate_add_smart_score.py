#!/usr/bin/env python3
"""
数据库迁移脚本：为news表添加smart_score字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """获取数据库URL"""
    return os.getenv('DATABASE_URL', 'postgresql://postgres:<your_password>@postgres.railway.internal:5432/railway')

def migrate_add_smart_score():
    """为news表添加smart_score字段"""
    try:
        # 获取数据库URL
        database_url = get_database_url()
        logger.info(f"连接到数据库: {database_url.split('@')[1] if '@' in database_url else database_url}")
        
        # 创建数据库引擎
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # 检查smart_score字段是否已存在
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'news' AND column_name = 'smart_score'
            """)
            
            result = conn.execute(check_query)
            if result.fetchone():
                logger.info("✅ smart_score字段已存在，跳过迁移")
                return True
            
            # 添加smart_score字段
            logger.info("🔧 开始添加smart_score字段...")
            
            alter_query = text("""
                ALTER TABLE news 
                ADD COLUMN smart_score DOUBLE PRECISION DEFAULT 0.0
            """)
            
            conn.execute(alter_query)
            conn.commit()
            
            logger.info("✅ smart_score字段添加成功")
            
            # 验证字段是否添加成功
            verify_query = text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns 
                WHERE table_name = 'news' AND column_name = 'smart_score'
            """)
            
            result = conn.execute(verify_query)
            column_info = result.fetchone()
            
            if column_info:
                logger.info(f"✅ 字段验证成功: {column_info}")
                return True
            else:
                logger.error("❌ 字段验证失败")
                return False
                
    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        return False

def update_existing_news_smart_score():
    """为现有新闻计算smart_score"""
    try:
        from app.db import SessionLocal
        from app.models import News
        from app.smart_scoring import compute_smart_score
        
        logger.info("🔄 开始为现有新闻计算smart_score...")
        
        db = SessionLocal()
        try:
            # 获取所有现有新闻
            existing_news = db.query(News).all()
            logger.info(f"📊 找到 {len(existing_news)} 条现有新闻")
            
            updated_count = 0
            for news in existing_news:
                try:
                    # 准备文章数据
                    article_data = {
                        'title': news.title,
                        'content': news.content,
                        'source': news.source or '',
                        'published_at': news.published_at or news.created_at,
                        'headline_count': news.headline_count or 0,
                        'summary_ai': news.summary_ai or {}
                    }
                    
                    # 计算智能评分
                    smart_score = compute_smart_score(article_data, [])
                    
                    # 更新数据库
                    news.smart_score = smart_score
                    updated_count += 1
                    
                    if updated_count % 50 == 0:
                        logger.info(f"🔄 已处理 {updated_count}/{len(existing_news)} 条新闻")
                        
                except Exception as e:
                    logger.warning(f"⚠️ 处理新闻 '{news.title[:50]}...' 时出错: {e}")
                    continue
            
            # 提交更改
            db.commit()
            logger.info(f"✅ 成功为 {updated_count} 条新闻计算smart_score")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ 更新现有新闻smart_score失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🚀 开始Smart Sort V2数据库迁移...")
    
    # 步骤1：添加smart_score字段
    if not migrate_add_smart_score():
        logger.error("❌ 添加smart_score字段失败")
        return False
    
    # 步骤2：为现有新闻计算smart_score
    if not update_existing_news_smart_score():
        logger.error("❌ 更新现有新闻smart_score失败")
        return False
    
    logger.info("✅ Smart Sort V2数据库迁移完成！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 