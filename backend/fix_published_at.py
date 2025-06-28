#!/usr/bin/env python3
"""
修复生产环境数据库中缺少published_at字段的新闻数据
"""

import requests
import json
from datetime import datetime, timedelta
import random

# 生产环境API地址
PRODUCTION_API = "https://simplenews-production.up.railway.app"

def check_database_status():
    """检查数据库状态"""
    try:
        print("🔍 检查数据库状态...")
        
        # 获取所有新闻
        response = requests.get(f"{PRODUCTION_API}/news/today?limit=100&sort_by=time")
        
        if response.status_code == 200:
            news_list = response.json()
            print(f"📰 数据库中共有 {len(news_list)} 条新闻")
            
            # 检查有多少条新闻缺少published_at
            missing_published_at = 0
            for news in news_list:
                if not news.get('published_at') or news.get('published_at') == 'N/A':
                    missing_published_at += 1
            
            print(f"❌ 缺少published_at的新闻: {missing_published_at} 条")
            print(f"✅ 有published_at的新闻: {len(news_list) - missing_published_at} 条")
            
            return missing_published_at > 0
        else:
            print(f"❌ 检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 检查异常: {e}")
        return False

def clean_and_refresh_news():
    """清理旧数据并重新抓取新闻"""
    try:
        print("\n🔄 开始清理和刷新新闻...")
        
        # 1. 清理重复新闻
        print("🧹 清理重复新闻...")
        response = requests.post(f"{PRODUCTION_API}/news/clean-duplicates")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 清理完成: {result.get('message', 'N/A')}")
        else:
            print(f"⚠️ 清理失败: {response.status_code}")
        
        # 2. 手动刷新新闻
        print("🔄 手动刷新新闻...")
        response = requests.post(f"{PRODUCTION_API}/news/refresh")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 刷新成功: {result.get('message', 'N/A')}")
            print(f"📊 获取到 {result.get('count', 0)} 条新闻")
        else:
            print(f"❌ 刷新失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 清理刷新异常: {e}")

def force_refresh_with_new_logic():
    """强制使用新的时间过滤逻辑刷新新闻"""
    try:
        print("\n🔄 强制刷新新闻（使用新的24小时过滤逻辑）...")
        
        # 多次刷新以确保获取最新数据
        for i in range(3):
            print(f"🔄 第 {i+1} 次刷新...")
            response = requests.post(f"{PRODUCTION_API}/news/refresh")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 第 {i+1} 次刷新成功: {result.get('count', 0)} 条新闻")
            else:
                print(f"❌ 第 {i+1} 次刷新失败: {response.status_code}")
            
            # 等待一下再继续
            import time
            time.sleep(2)
            
    except Exception as e:
        print(f"❌ 强制刷新异常: {e}")

def main():
    print("=" * 60)
    print("🔧 生产环境新闻数据修复工具")
    print("=" * 60)
    
    # 检查当前状态
    needs_fix = check_database_status()
    
    if needs_fix:
        print("\n" + "-" * 60)
        print("⚠️  检测到数据库中有新闻缺少published_at字段")
        print("建议执行以下修复步骤:")
        print("1. 清理重复新闻")
        print("2. 重新抓取新闻（使用新的24小时过滤逻辑）")
        print("3. 验证修复结果")
        
        user_input = input("\n是否要执行修复? (y/N): ").strip().lower()
        
        if user_input in ['y', 'yes']:
            # 执行修复
            clean_and_refresh_news()
            
            # 强制刷新
            force_refresh_with_new_logic()
            
            # 验证修复结果
            print("\n" + "-" * 60)
            print("🔍 验证修复结果...")
            check_database_status()
        else:
            print("❌ 取消修复")
    else:
        print("\n✅ 数据库状态正常，所有新闻都有published_at字段")
        
        # 询问是否要刷新新闻
        user_input = input("\n是否要刷新新闻以获取最新数据? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            force_refresh_with_new_logic()
            print("\n" + "-" * 60)
            print("🔍 验证刷新结果...")
            check_database_status()

if __name__ == "__main__":
    main() 