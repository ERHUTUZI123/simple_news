"""
Smart Sort V2 - 评分配置模块
定义各种评分的权重、关键词映射和配置参数
"""

# 权重配置
WEIGHTS = {
    'significance': 0.3,    # 事件影响力
    'freshness': 0.2,       # 时效性
    'source_weight': 0.15,  # 来源可信度
    'popularity': 0.1,      # 流行度
    'novelty': 0.15,        # 新颖性
    'summary_quality': 0.1  # 摘要质量
}

# 重要性关键词映射（Significance Score）
SIGNIFICANCE_KEYWORDS = {
    # 10分 - 重大国际政治事件、战争、重大科技突破
    10: [
        'war', 'conflict', 'invasion', 'attack', 'missile', 'nuclear', 'weapon',
        'president', 'prime minister', 'election', 'vote', 'referendum',
        'breakthrough', 'discovery', 'invention', 'innovation', 'revolutionary',
        'crisis', 'emergency', 'disaster', 'catastrophe', 'pandemic', 'epidemic'
    ],
    
    # 8-9分 - 经济政策、重要选举、重大自然灾害
    8: [
        'economy', 'economic', 'policy', 'regulation', 'law', 'bill', 'act',
        'election', 'campaign', 'candidate', 'political', 'government',
        'earthquake', 'tsunami', 'hurricane', 'tornado', 'flood', 'wildfire',
        'trade', 'tariff', 'sanction', 'embargo', 'diplomatic', 'treaty'
    ],
    
    # 6-7分 - 商业并购、体育重大赛事、娱乐重大事件
    6: [
        'merger', 'acquisition', 'takeover', 'deal', 'agreement', 'partnership',
        'olympics', 'world cup', 'championship', 'tournament', 'final',
        'award', 'oscar', 'grammy', 'nobel', 'prize', 'celebration',
        'business', 'corporate', 'company', 'stock', 'market', 'investment'
    ],
    
    # 4-5分 - 一般商业新闻、地方政治
    4: [
        'local', 'city', 'town', 'community', 'neighborhood', 'district',
        'business', 'company', 'startup', 'funding', 'venture', 'capital',
        'technology', 'software', 'app', 'platform', 'service', 'product'
    ],
    
    # 1-3分 - 娱乐八卦、生活新闻
    1: [
        'celebrity', 'star', 'actor', 'actress', 'singer', 'musician',
        'gossip', 'rumor', 'scandal', 'divorce', 'marriage', 'wedding',
        'lifestyle', 'fashion', 'beauty', 'food', 'recipe', 'travel'
    ]
}

# 来源权重映射（Source Weight Score）
SOURCE_WEIGHTS = {
    # 10分 - 顶级权威媒体
    10: [
        'Financial Times', 'The New York Times', 'Reuters', 'Associated Press',
        'AP', 'AP News'
    ],
    
    # 9分 - 知名国际媒体
    9: [
        'BBC News', 'BBC', 'The Washington Post', 'The Guardian'
    ],
    
    # 8分 - 专业财经媒体
    8: [
        'Bloomberg', 'CNBC', 'Los Angeles Times'
    ],
    
    # 7分 - 主流电视媒体
    7: [
        'NBC News', 'CBS News', 'ABC News'
    ],
    
    # 6分 - 其他知名媒体
    6: [
        'Fox News', 'Sky News', 'The Telegraph'
    ],
    
    # 5分 - 国际媒体
    5: [
        'The Independent', 'Euronews', 'Deutsche Welle'
    ],
    
    # 4分 - 地区媒体
    4: [
        'Al Jazeera', 'Axios'
    ],
    
    # 3分 - 其他一般媒体
    3: [
        'other', 'unknown', 'blog', 'social'
    ]
}

# 时效性评分配置（Freshness Score）
FRESHNESS_CONFIG = {
    '3_hours': 10,    # 3小时内
    '6_hours': 7,     # 6小时内
    '12_hours': 5,    # 12小时内
    '24_hours': 3,    # 24小时内
    '48_hours': 1,    # 48小时内
    'beyond': 0       # 48小时以上
}

# 流行度评分配置（Popularity Score）
POPULARITY_CONFIG = {
    'no_votes': 0,        # 无点赞
    'low_votes': 3,       # 1-5个点赞
    'medium_votes': 6,    # 6-10个点赞
    'high_votes': 10,     # 10个以上点赞
    'duplicate_bonus': 2  # 被多个源报道的额外加分
}

# 摘要质量评分配置（Summary Quality Score）
SUMMARY_QUALITY_CONFIG = {
    'excellent': 10,  # 结构完整，逻辑清晰
    'good': 8,        # 结构良好
    'fair': 6,        # 结构一般
    'poor': 3,        # 结构较差
    'none': 0         # 无摘要
}

# 标题相似度阈值（Novelty Score）
SIMILARITY_THRESHOLDS = {
    'exact_match': 0.95,    # 完全重复
    'high_similar': 0.8,    # 高度相似
    'medium_similar': 0.6,  # 中等相似
    'low_similar': 0.3,     # 轻微相似
    'unique': 0.1           # 独特
}

def get_significance_keywords():
    """获取重要性关键词映射"""
    return SIGNIFICANCE_KEYWORDS

def get_source_weights():
    """获取来源权重映射"""
    return SOURCE_WEIGHTS

def get_freshness_config():
    """获取时效性配置"""
    return FRESHNESS_CONFIG

def get_popularity_config():
    """获取流行度配置"""
    return POPULARITY_CONFIG

def get_summary_quality_config():
    """获取摘要质量配置"""
    return SUMMARY_QUALITY_CONFIG

def get_similarity_thresholds():
    """获取相似度阈值"""
    return SIMILARITY_THRESHOLDS

def get_weights():
    """获取权重配置"""
    return WEIGHTS 