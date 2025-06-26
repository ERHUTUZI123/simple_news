import math
from datetime import datetime
from typing import List, Dict, Any

# 新闻源权重配置
SOURCE_RATINGS = {
    "Financial Times": 5,
    "Wall Street Journal": 5,
    "WSJ": 5,
    "Reuters": 4,
    "AP": 4,
    "AP News": 4,
    "BBC": 4,
    "CNN": 3,
    "The Guardian": 3,
    "NYTimes": 4,
    "The New York Times": 4,
    "Bloomberg": 4,
    "Al Jazeera": 3,
    "NPR": 3,
    "Fox News": 2,
    "Sky News": 3,
    "TechCrunch": 3,
    "Ars Technica": 3,
    "Wired": 3,
    "The Verge": 3,
    "Engadget": 2,
    "Gizmodo": 2,
    "Mashable": 2,
    "VentureBeat": 3,
    "CNET": 2,
}

def time_decay_weight(published_at: datetime) -> float:
    """时间衰减权重，半衰期12小时"""
    now = datetime.utcnow()
    hours_since = (now - published_at).total_seconds() / 3600
    return math.exp(-hours_since / 12)

def ai_structure_score(summary_ai: Dict[str, Any]) -> float:
    """AI摘要结构评分，1-5分"""
    if not summary_ai:
        return 3.0  # 默认中值
    
    structure_score = summary_ai.get('structure_score', 3.0)
    return max(1.0, min(5.0, structure_score))  # 确保在1-5范围内

def source_weight(source: str) -> float:
    """新闻源权重评分"""
    rating = SOURCE_RATINGS.get(source, 2)  # 默认权重2
    return rating / 5.0

def keyword_novelty_score(keywords: List[str], existing_keyword_map: Dict[str, int]) -> float:
    """关键词新颖度评分"""
    if not keywords:
        return 0.5  # 无关键词时给中等分数
    
    score = 0
    for keyword in keywords:
        if keyword.lower() not in existing_keyword_map:
            score += 1
    
    return score / len(keywords)

def headline_count_score(count: int) -> float:
    """点赞数归一化评分"""
    return min(count / 20.0, 1.0)  # 超过20上限归一为1

def calculate_news_score(
    published_at: datetime,
    summary_ai: Dict[str, Any],
    source: str,
    keywords: List[str],
    headline_count: int,
    existing_keyword_map: Dict[str, int]
) -> float:
    """计算新闻综合评分"""
    
    # 各项评分
    time_score = time_decay_weight(published_at) * 0.4
    ai_score = ai_structure_score(summary_ai) * 0.2
    source_score = source_weight(source) * 0.15
    novelty_score = keyword_novelty_score(keywords, existing_keyword_map) * 0.15
    headline_score = headline_count_score(headline_count) * 0.1
    
    # 综合评分
    total_score = time_score + ai_score + source_score + novelty_score + headline_score
    
    return round(total_score, 3)

def extract_keywords_from_text(text: str, max_keywords: int = 5) -> List[str]:
    """从文本中提取关键词（简化版本）"""
    # 这里可以集成更复杂的关键词提取算法
    # 目前使用简单的词频统计
    import re
    from collections import Counter
    
    # 清理文本
    text = re.sub(r'[^\w\s]', '', text.lower())
    words = text.split()
    
    # 过滤停用词
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'
    }
    
    # 统计词频
    word_counts = Counter(word for word in words if word not in stop_words and len(word) > 3)
    
    # 返回最常见的几个词作为关键词
    return [word for word, count in word_counts.most_common(max_keywords)]

def build_existing_keyword_map(news_list: List[Dict]) -> Dict[str, int]:
    """构建现有新闻的关键词频率映射"""
    keyword_map = {}
    for news in news_list:
        keywords = news.get('keywords', [])
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_map[keyword_lower] = keyword_map.get(keyword_lower, 0) + 1
    return keyword_map 