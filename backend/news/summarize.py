import hashlib
import os
import json
import openai
from typing import Dict, Any

CACHE_DIR = "/tmp/news_summary_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def summarize_news(text: str, summary_type: str = "brief") -> Dict[str, Any]:
    """
    生成新闻摘要，支持brief和detailed两种类型
    返回包含摘要和结构评分的字典
    """
    # 用正文内容和类型做哈希
    cache_key = f"{text}_{summary_type}"
    key = hashlib.md5(cache_key.encode("utf-8")).hexdigest()
    cache_path = os.path.join(CACHE_DIR, key + ".json")
    
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)

    # 根据类型设置不同的提示词
    if summary_type == "brief":
        prompt = f"""
        请为以下新闻生成一个简洁的摘要，要求：
        1. 2-3句话，约150-200字符
        2. 突出核心事实和关键信息
        3. 使用客观、准确的表述
        4. 避免主观评论
        
        新闻内容：
        {text}
        
        请只返回摘要内容，不要其他解释。
        """
        max_tokens = 100
    else:  # detailed
        prompt = f"""
        请为以下新闻生成一个详细的摘要，要求：
        1. 420+字符，65+单词
        2. 包含背景信息、影响分析
        3. 结构清晰，逻辑连贯
        4. 提供深度洞察
        
        新闻内容：
        {text}
        
        请只返回摘要内容，不要其他解释。
        """
        max_tokens = 300

    try:
        # 调用OpenAI API
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip() if response.choices[0].message.content else "摘要生成失败"
        
        # 计算结构评分（简化版本）
        structure_score = calculate_structure_score(summary, summary_type)
        
        result = {
            "summary": summary,
            "structure_score": structure_score
        }
        
        # 缓存结果
        with open(cache_path, "w") as f:
            json.dump(result, f)
        
        return result
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        # 返回默认结果
        return {
            "summary": "摘要生成失败",
            "structure_score": 3.0
        }

def calculate_structure_score(summary: str, summary_type: str) -> float:
    """
    计算摘要的结构评分（1-5分）
    基于长度、完整性、逻辑性等因素
    """
    score = 3.0  # 基础分
    
    # 长度评分
    char_count = len(summary)
    word_count = len(summary.split())
    
    if summary_type == "brief":
        if 150 <= char_count <= 200 and 20 <= word_count <= 30:
            score += 1.0
        elif 100 <= char_count <= 250 and 15 <= word_count <= 35:
            score += 0.5
    else:  # detailed
        if char_count >= 420 and word_count >= 65:
            score += 1.0
        elif char_count >= 300 and word_count >= 50:
            score += 0.5
    
    # 结构完整性评分
    if "." in summary and len(summary.split(".")) >= 2:
        score += 0.5
    
    # 关键词覆盖评分
    important_words = ["因为", "所以", "但是", "然而", "此外", "同时", "因此"]
    if any(word in summary for word in important_words):
        score += 0.5
    
    return min(5.0, max(1.0, score))

def generate_both_summaries(text: str) -> Dict[str, Any]:
    """
    生成brief和detailed两种摘要
    """
    brief_result = summarize_news(text, "brief")
    detailed_result = summarize_news(text, "detailed")
    
    return {
        "brief": brief_result["summary"],
        "detailed": detailed_result["summary"],
        "structure_score": (brief_result["structure_score"] + detailed_result["structure_score"]) / 2
    }


