"""
Smart Sort V2 - 评分配置模块（改进版）
参考专业新闻网站的评分标准，使用更合理的评分范围
"""

# 权重配置（保持原有权重）
WEIGHTS = {
    'significance': 0.3,    # 事件影响力
    'freshness': 0.2,       # 时效性
    'source_weight': 0.15,  # 来源可信度
    'popularity': 0.1,      # 流行度
    'novelty': 0.15,        # 新颖性
    'summary_quality': 0.1  # 摘要质量
}

# 重要性关键词映射（改进版，参考专业新闻标准）
SIGNIFICANCE_KEYWORDS = {
    # 6.5分 - 重大国际政治事件、战争、重大科技突破
    6.5: [
        'war', 'conflict', 'invasion', 'attack', 'missile', 'nuclear', 'weapon',
        'president', 'prime minister', 'election', 'vote', 'referendum',
        'breakthrough', 'discovery', 'invention', 'innovation', 'revolutionary',
        'crisis', 'emergency', 'disaster', 'catastrophe', 'pandemic', 'epidemic',
        'trump', 'biden', 'putin', 'nato', 'supreme court', 'congress'
    ],
    
    # 6.4分 - 重要国际协议、经济政策、重大自然灾害
    6.4: [
        'economy', 'economic', 'policy', 'regulation', 'law', 'bill', 'act',
        'election', 'campaign', 'candidate', 'political', 'government',
        'earthquake', 'tsunami', 'hurricane', 'tornado', 'flood', 'wildfire',
        'trade', 'tariff', 'sanction', 'embargo', 'diplomatic', 'treaty',
        'agreement', 'deal', 'peace', 'ceasefire', 'negotiation'
    ],
    
    # 6.3分 - 政策变化、科技突破、商业并购
    6.3: [
        'merger', 'acquisition', 'takeover', 'deal', 'agreement', 'partnership',
        'olympics', 'world cup', 'championship', 'tournament', 'final',
        'award', 'oscar', 'grammy', 'nobel', 'prize', 'celebration',
        'business', 'corporate', 'company', 'stock', 'market', 'investment',
        'ai', 'artificial intelligence', 'technology', 'innovation', 'copyright'
    ],
    
    # 6.2分 - 国际关系、科技新闻、地区冲突
    6.2: [
        'international', 'foreign', 'diplomatic', 'relations', 'alliance',
        'technology', 'software', 'app', 'platform', 'service', 'product',
        'conflict', 'tension', 'dispute', 'protest', 'demonstration',
        'virus', 'infection', 'health', 'medical', 'research'
    ],
    
    # 6.1分 - 地区性重要新闻、一般商业新闻
    6.1: [
        'local', 'city', 'town', 'community', 'neighborhood', 'district',
        'business', 'company', 'startup', 'funding', 'venture', 'capital',
        'technology', 'software', 'app', 'platform', 'service', 'product',
        'regional', 'provincial', 'state', 'county'
    ],
    
    # 6.0分 - 娱乐八卦、生活新闻
    6.0: [
        'celebrity', 'star', 'actor', 'actress', 'singer', 'musician',
        'gossip', 'rumor', 'scandal', 'divorce', 'marriage', 'wedding',
        'lifestyle', 'fashion', 'beauty', 'food', 'recipe', 'travel'
    ]
}

# 来源权重映射（改进版，更细致的评分）
SOURCE_WEIGHTS = {
    # 6.5分 - 顶级权威媒体
    6.5: [
        'Financial Times', 'The New York Times', 'Reuters', 'Associated Press',
        'AP', 'AP News', 'BBC News', 'BBC'
    ],
    
    # 6.4分 - 知名国际媒体
    6.4: [
        'The Washington Post', 'The Guardian', 'Bloomberg', 'CNBC'
    ],
    
    # 6.3分 - 专业财经媒体
    6.3: [
        'Los Angeles Times', 'NBC News', 'CBS News', 'ABC News'
    ],
    
    # 6.2分 - 其他知名媒体
    6.2: [
        'Fox News', 'Sky News', 'The Telegraph', 'The Independent'
    ],
    
    # 6.1分 - 国际媒体
    6.1: [
        'Euronews', 'Deutsche Welle', 'Al Jazeera', 'Axios'
    ],
    
    # 6.0分 - 其他一般媒体
    6.0: [
        'other', 'unknown', 'blog', 'social'
    ]
}

# 时效性评分配置（改进版，更细致的时效性处理）
FRESHNESS_CONFIG = {
    '1_hour': 6.5,     # 1小时内
    '3_hours': 6.4,    # 3小时内
    '6_hours': 6.3,    # 6小时内
    '12_hours': 6.2,   # 12小时内
    '24_hours': 6.1,   # 24小时内
    '48_hours': 6.0,   # 48小时内
    'beyond': 5.9      # 48小时以上
}

# 流行度评分配置（改进版）
POPULARITY_CONFIG = {
    'no_votes': 6.0,       # 无点赞
    'low_votes': 6.1,      # 1-5个点赞
    'medium_votes': 6.2,   # 6-10个点赞
    'high_votes': 6.3,     # 10个以上点赞
    'duplicate_bonus': 0.1 # 被多个源报道的额外加分
}

# 摘要质量评分配置（改进版）
SUMMARY_QUALITY_CONFIG = {
    'excellent': 6.5,  # 结构完整，逻辑清晰
    'good': 6.3,       # 结构良好
    'fair': 6.1,       # 结构一般
    'poor': 6.0,       # 结构较差
    'none': 5.9        # 无摘要
}

# 标题相似度阈值（改进版）
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