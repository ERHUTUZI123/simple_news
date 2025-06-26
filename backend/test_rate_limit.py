#!/usr/bin/env python3
"""
测试速率限制处理功能
"""
import requests
import time
import json

# 配置
API_BASE = "http://localhost:8000"
TEST_TEXT = """
Artificial Intelligence (AI) has emerged as one of the most transformative technologies of the 21st century. 
From machine learning algorithms that power recommendation systems to natural language processing that enables 
chatbots and virtual assistants, AI is reshaping industries across the globe. In healthcare, AI is being used 
to diagnose diseases, predict patient outcomes, and accelerate drug discovery. In finance, it's revolutionizing 
trading strategies, fraud detection, and risk assessment. The automotive industry is leveraging AI for autonomous 
vehicles, while retail companies are using it for inventory management and personalized shopping experiences.

However, the rapid advancement of AI also raises important questions about ethics, privacy, and the future of work. 
As AI systems become more sophisticated, concerns about job displacement, algorithmic bias, and data privacy have 
grown. Experts emphasize the need for responsible AI development that prioritizes human well-being and addresses 
potential risks. Governments and organizations worldwide are developing frameworks and regulations to ensure AI 
is developed and deployed ethically.

The future of AI holds immense promise, but it requires careful consideration of both its benefits and challenges. 
Success will depend on collaboration between technologists, policymakers, and society at large to create AI systems 
that enhance human capabilities while maintaining human values and dignity.
"""

def test_summary_rate_limit():
    """测试摘要生成的速率限制"""
    print("🧪 测试摘要生成速率限制...")
    
    success_count = 0
    failure_count = 0
    
    for i in range(10):
        try:
            response = requests.post(
                f"{API_BASE}/news/summary",
                json={"content": TEST_TEXT},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 摘要生成成功: {result['summary'][:100]}...")
                success_count += 1
            else:
                print(f"❌ 摘要生成失败: {response.status_code} - {response.text}")
                failure_count += 1
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            failure_count += 1
        
        # 短暂延迟
        time.sleep(1)
    
    print(f"\n📊 摘要测试结果: 成功 {success_count}, 失败 {failure_count}")

def test_news_fetch():
    """测试新闻获取"""
    print("\n🧪 测试新闻获取...")
    
    try:
        response = requests.get(f"{API_BASE}/news/today?limit=5")
        
        if response.status_code == 200:
            news_list = response.json()
            print(f"✅ 成功获取 {len(news_list)} 条新闻")
            
            for i, news in enumerate(news_list):
                print(f"  {i+1}. {news['title'][:50]}... (投票: {news.get('vote_count', 0)})")
        else:
            print(f"❌ 新闻获取失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("🚀 开始API速率限制测试...\n")
    
    test_summary_rate_limit()
    test_news_fetch()
    
    print("\n✨ 测试完成!") 