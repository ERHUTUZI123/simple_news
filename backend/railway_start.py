#!/usr/bin/env python3
"""
Railway启动脚本
同时运行FastAPI服务器和定时任务
"""

import subprocess
import sys
import os
import threading
import time
from cache_worker import refresh_news_cache

def run_fastapi():
    """运行FastAPI服务器"""
    print("🚀 启动FastAPI服务器...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", os.getenv("PORT", "8000")
    ])

def run_scheduler():
    """运行定时任务"""
    print("⏰ 启动定时任务...")
    while True:
        try:
            print("🔄 定时任务：开始刷新新闻...")
            refresh_news_cache()
            print("✅ 定时任务：新闻刷新完成")
        except Exception as e:
            print(f"❌ 定时任务：新闻刷新失败 - {e}")
        
        # 等待15分钟
        time.sleep(15 * 60)

if __name__ == "__main__":
    # 启动定时任务线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # 运行FastAPI服务器
    run_fastapi() 