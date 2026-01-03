"""
Smart Sort V2 - Ratings Config
"""

# weights distribution
WEIGHTS = {
    'significance': 0.3,    
    'freshness': 0.2,       
    'source_weight': 0.15,  
    'popularity': 0.1,      
    'novelty': 0.15,        
    'summary_quality': 0.1 
}

# significance
SIGNIFICANCE_KEYWORDS = {
    # 10 - Significant international politics, war and technology things
    10: [
        'war', 'conflict', 'invasion', 'attack', 'missile', 'nuclear', 'weapon',
        'president', 'prime minister', 'election', 'vote', 'referendum',
        'breakthrough', 'discovery', 'invention', 'innovation', 'revolutionary',
        'crisis', 'emergency', 'disaster', 'catastrophe', 'pandemic', 'epidemic',
        'trump', 'biden', 'putin', 'nato', 'supreme court', 'congress', 'chips',
        'semiconductor'
    ],
    
    # 8 - Important international meetings, economics policies, natural disasters
    8: [
        'economy', 'economic', 'policy', 'regulation', 'law', 'bill', 'act',
        'election', 'campaign', 'candidate', 'political', 'government',
        'earthquake', 'tsunami', 'hurricane', 'tornado', 'flood', 'wildfire',
        'trade', 'tariff', 'sanction', 'embargo', 'diplomatic', 'treaty',
        'agreement', 'deal', 'peace', 'ceasefire', 'negotiation'
    ],
    
    # 6 - less important policies changes, tech breakthroughs, commercial things
    6: [
        'merger', 'acquisition', 'takeover', 'deal', 'agreement', 'partnership',
        'olympics', 'world cup', 'championship', 'tournament', 'final',
        'award', 'oscar', 'grammy', 'nobel', 'prize', 'celebration',
        'business', 'corporate', 'company', 'stock', 'market', 'investment',
        'ai', 'artificial intelligence', 'technology', 'innovation', 'copyright'
    ],
    
    # 4 - local news
    4: [
        'local', 'city', 'town', 'community', 'neighborhood', 'district',
        'business', 'company', 'startup', 'funding', 'venture', 'capital',
        'technology', 'software', 'app', 'platform', 'service', 'product',
        'regional', 'provincial', 'state', 'county'
    ],
    
    # 2 - less important news
    2: [
        'celebrity', 'star', 'actor', 'actress', 'singer', 'musician',
        'gossip', 'rumor', 'scandal', 'divorce', 'marriage', 'wedding',
        'lifestyle', 'fashion', 'beauty', 'food', 'recipe', 'travel'
    ]
}

# Source
SOURCE_WEIGHTS = {
    # 10 top media
    10: [
        'Financial Times', 'The New York Times', 'Reuters', 'Associated Press',
        'AP', 'AP News', 'BBC News', 'BBC', 'CNN', 'NBC News', 'CBS News', 
        'ABC News'
    ],
    
    # 8 known media
    8: [
        'The Washington Post', 'The Guardian', 'Bloomberg', 'CNBC'
    ],
    
    # 6 professional media
    6: [
        'Los Angeles Times'
    ],
    
    # 4 other media
    4: [
        'Fox News', 'Sky News', 'The Telegraph', 'The Independent'
    ],
    
    # 2 - international media
    2: [
        'Euronews', 'Deutsche Welle', 'Al Jazeera', 'Axios', 'CGTN'
    ],
    
    # 0 - random media
    0: [
        'other', 'unknown', 'blog', 'social'
    ]
}

# freshness 
FRESHNESS_CONFIG = {
    '1_hour': 10,     # within 1 hr
    '3_hours': 8.5,    # within 3 hrs
    '6_hours': 7.0,    # within 6 hrs
    '12_hours': 5.5,   # within 12 hrs
    '24_hours': 4,   # within 24 hrs
    '48_hours': 2.5,   # within 48 hrs
    'beyond': 1      # over 48 hrs
}

# popularity
POPULARITY_CONFIG = {
    'no_votes': 6.0,       # no vote
    'low_votes': 6.1,      # 1-5 votes
    'medium_votes': 6.2,   # 6-10 votes
    'high_votes': 6.3,     # over 10 votes
    'duplicate_bonus': 0.1 # muti sources bonus
}

# summary quality
SUMMARY_QUALITY_CONFIG = {
    'excellent': 10,  # well organized and logical
    'good': 8,       # well organized
    'fair': 6,       # averagely organized
    'poor': 2,       # badly organized
    'none': 0        # no summary
}

# similarity thresholds
SIMILARITY_THRESHOLDS = {
    'exact_match': 0.95,    # 100%
    'high_similar': 0.8,    # highly similar
    'medium_similar': 0.6,  # similar
    'low_similar': 0.3,     # slightly similar
    'unique': 0.1           # unique
}

def get_significance_keywords():
    """Get significance keywords mapping"""
    return SIGNIFICANCE_KEYWORDS

def get_source_weights():
    """Get source weights mapping"""
    return SOURCE_WEIGHTS

def get_freshness_config():
    """Get freshness configuration"""
    return FRESHNESS_CONFIG

def get_popularity_config():
    """Get popularity configuration"""
    return POPULARITY_CONFIG

def get_summary_quality_config():
    """Get summary quality configuration"""
    return SUMMARY_QUALITY_CONFIG

def get_similarity_thresholds():
    """Get similarity thresholds"""
    return SIMILARITY_THRESHOLDS

def get_weights():
    """Get weights configuration"""
    return WEIGHTS 