"""
Smart Sort V2 - 智能评分模块
实现多维度新闻评分算法，包括重要性、时效性、来源可信度、流行度、新颖性和摘要质量
"""

import re
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
from .scoring_config import (
    get_significance_keywords, get_source_weights, get_freshness_config,
    get_popularity_config, get_summary_quality_config, get_similarity_thresholds,
    get_weights
)

def normalize_score(score: float, min_val: float = 5.9, max_val: float = 6.5) -> float:
    """
    标准化分数到指定范围（改进版）
    
    Args:
        score: 原始分数
        min_val: 最小值
        max_val: 最大值
    
    Returns:
        标准化后的分数
    """
    if score < min_val:
        return min_val
    elif score > max_val:
        return max_val
    return score

def compute_significance_score(title: str, content: str) -> float:
    """
    计算事件影响力分数（改进版）
    
    Args:
        title: 新闻标题
        content: 新闻内容
    
    Returns:
        重要性分数 (6.0-6.5)
    """
    # 合并标题和内容进行关键词匹配
    text = f"{title} {content}".lower()
    
    # 获取重要性关键词映射
    significance_keywords = get_significance_keywords()
    
    # 计算最高匹配分数
    max_score = 6.0  # 默认最低分
    
    for score, keywords in significance_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text:
                max_score = max(max_score, score)
                break  # 找到该分数段的匹配就跳出
    
    return normalize_score(max_score, 6.0, 6.5)

def compute_freshness_score(published_at: datetime) -> float:
    """
    计算时效性分数（改进版）
    
    Args:
        published_at: 发布时间
    
    Returns:
        时效性分数 (5.9-6.5)
    """
    now = datetime.utcnow()
    time_diff = now - published_at
    hours_diff = time_diff.total_seconds() / 3600
    
    # 获取时效性配置
    freshness_config = get_freshness_config()
    
    if hours_diff <= 1:
        return freshness_config['1_hour']
    elif hours_diff <= 3:
        return freshness_config['3_hours']
    elif hours_diff <= 6:
        return freshness_config['6_hours']
    elif hours_diff <= 12:
        return freshness_config['12_hours']
    elif hours_diff <= 24:
        return freshness_config['24_hours']
    elif hours_diff <= 48:
        return freshness_config['48_hours']
    else:
        return freshness_config['beyond']

def compute_source_weight_score(source: str) -> float:
    """
    计算来源可信度分数（改进版）
    
    Args:
        source: 新闻来源
    
    Returns:
        来源权重分数 (6.0-6.5)
    """
    source_weights = get_source_weights()
    
    # 查找匹配的来源权重
    for score, sources in source_weights.items():
        if source in sources:
            return score
    
    # 如果没有找到匹配，返回默认值
    return 6.0

def compute_popularity_score(headline_count: int, duplicate_count: int = 0) -> float:
    """
    计算流行度分数（改进版）
    
    Args:
        headline_count: 点赞数
        duplicate_count: 重复报道数
    
    Returns:
        流行度分数 (6.0-6.3)
    """
    popularity_config = get_popularity_config()
    
    # 基于点赞数的分数
    if headline_count == 0:
        base_score = popularity_config['no_votes']
    elif headline_count <= 5:
        base_score = popularity_config['low_votes']
    elif headline_count <= 10:
        base_score = popularity_config['medium_votes']
    else:
        base_score = popularity_config['high_votes']
    
    # 重复报道的额外加分
    duplicate_bonus = duplicate_count * popularity_config['duplicate_bonus']
    
    total_score = base_score + duplicate_bonus
    return normalize_score(total_score, 6.0, 6.3)

def calculate_title_similarity(title1: str, title2: str) -> float:
    """
    计算两个标题的相似度
    
    Args:
        title1: 标题1
        title2: 标题2
    
    Returns:
        相似度分数 (0-1)
    """
    # 使用SequenceMatcher计算相似度
    similarity = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
    return similarity

def compute_novelty_score(title: str, existing_titles: List[str]) -> float:
    """
    计算新颖性分数（改进版）
    
    Args:
        title: 当前新闻标题
        existing_titles: 已存在的新闻标题列表
    
    Returns:
        新颖性分数 (5.9-6.5)
    """
    if not existing_titles:
        return 6.5  # 如果没有已存在的新闻，认为完全新颖
    
    # 计算与所有已存在标题的最大相似度
    max_similarity = 0
    for existing_title in existing_titles:
        similarity = calculate_title_similarity(title, existing_title)
        max_similarity = max(max_similarity, similarity)
    
    # 根据相似度计算新颖性分数
    similarity_thresholds = get_similarity_thresholds()
    
    if max_similarity >= similarity_thresholds['exact_match']:
        return 5.9  # 完全重复
    elif max_similarity >= similarity_thresholds['high_similar']:
        return 6.0  # 高度相似
    elif max_similarity >= similarity_thresholds['medium_similar']:
        return 6.1  # 中等相似
    elif max_similarity >= similarity_thresholds['low_similar']:
        return 6.2  # 轻微相似
    else:
        return 6.5  # 独特

def compute_summary_quality_score(summary_ai: Dict[str, Any]) -> float:
    """
    计算摘要质量分数（改进版）
    
    Args:
        summary_ai: AI摘要结构
    
    Returns:
        摘要质量分数 (5.9-6.5)
    """
    if not summary_ai:
        return 5.9
    
    # 获取结构评分
    structure_score = summary_ai.get('structure_score', 0)
    
    # 将结构评分映射到摘要质量分数
    summary_quality_config = get_summary_quality_config()
    
    if structure_score >= 8:
        return summary_quality_config['excellent']
    elif structure_score >= 6:
        return summary_quality_config['good']
    elif structure_score >= 4:
        return summary_quality_config['fair']
    elif structure_score >= 1:
        return summary_quality_config['poor']
    else:
        return summary_quality_config['none']

def compute_smart_score(
    article: Dict[str, Any],
    existing_news: List[Dict[str, Any]] = None
) -> float:
    """
    计算综合智能评分（改进版）
    
    Args:
        article: 新闻文章数据
        existing_news: 已存在的新闻列表（用于计算新颖性）
    
    Returns:
        综合智能评分 (5.9-6.5)
    """
    if existing_news is None:
        existing_news = []
    
    # 获取权重配置
    weights = get_weights()
    
    # 提取文章数据
    title = article.get('title', '')
    content = article.get('content', '')
    source = article.get('source', '')
    published_at = article.get('published_at')
    headline_count = article.get('headline_count', 0)
    summary_ai = article.get('summary_ai', {})
    
    # 计算各维度分数
    significance_score = compute_significance_score(title, content)
    freshness_score = compute_freshness_score(published_at) if published_at else 6.0
    source_weight_score = compute_source_weight_score(source)
    popularity_score = compute_popularity_score(headline_count)
    
    # 计算新颖性分数
    existing_titles = [news.get('title', '') for news in existing_news]
    novelty_score = compute_novelty_score(title, existing_titles)
    
    # 计算摘要质量分数
    summary_quality_score = compute_summary_quality_score(summary_ai)
    
    # 计算加权总分
    smart_score = (
        weights['significance'] * significance_score +
        weights['freshness'] * freshness_score +
        weights['source_weight'] * source_weight_score +
        weights['popularity'] * popularity_score +
        weights['novelty'] * novelty_score +
        weights['summary_quality'] * summary_quality_score
    )
    
    return normalize_score(smart_score, 5.9, 6.5)

def compute_smart_score_batch(
    articles: List[Dict[str, Any]],
    existing_news: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    批量计算智能评分
    
    Args:
        articles: 新闻文章列表
        existing_news: 已存在的新闻列表
    
    Returns:
        包含智能评分的新闻列表
    """
    if existing_news is None:
        existing_news = []
    
    # 为每篇文章计算智能评分
    for article in articles:
        smart_score = compute_smart_score(article, existing_news)
        article['smart_score'] = smart_score
    
    # 按智能评分排序
    articles.sort(key=lambda x: x.get('smart_score', 0), reverse=True)
    
    return articles

def get_score_breakdown(article: Dict[str, Any], existing_news: List[Dict[str, Any]] = None) -> Dict[str, float]:
    """
    获取评分详细分解
    
    Args:
        article: 新闻文章数据
        existing_news: 已存在的新闻列表
    
    Returns:
        各维度评分详情
    """
    if existing_news is None:
        existing_news = []
    
    title = article.get('title', '')
    content = article.get('content', '')
    source = article.get('source', '')
    published_at = article.get('published_at')
    headline_count = article.get('headline_count', 0)
    summary_ai = article.get('summary_ai', {})
    existing_titles = [news.get('title', '') for news in existing_news]
    
    return {
        'significance': compute_significance_score(title, content),
        'freshness': compute_freshness_score(published_at) if published_at else 0,
        'source_weight': compute_source_weight_score(source),
        'popularity': compute_popularity_score(headline_count),
        'novelty': compute_novelty_score(title, existing_titles),
        'summary_quality': compute_summary_quality_score(summary_ai),
        'smart_score': compute_smart_score(article, existing_news)
    } 