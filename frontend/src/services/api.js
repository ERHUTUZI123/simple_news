const API_BASE = "https://simplenews-production.up.railway.app";

// 获取新闻列表（只支持时间排序）
export const fetchNewsWithSort = async (offset = 0, limit = 10, sourceFilter = '') => {
  try {
    const params = new URLSearchParams({
      offset: offset.toString(),
      limit: limit.toString(),
    });
    
    if (sourceFilter) {
      params.append('source', sourceFilter);
    }
    
    const response = await fetch(`${API_BASE}/news?${params}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.news || [];
  } catch (error) {
    console.error('Error fetching news:', error);
    return [];
  }
};

// 投票功能
export const voteNews = async (title, delta) => {
  try {
    const params = new URLSearchParams({
      title: title,
      delta: delta.toString()
    });
    
    const response = await fetch(`${API_BASE}/news/vote?${params}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error voting for news:', error);
    throw error;
  }
};

// 获取投票数
export const getVoteCount = async (title) => {
  try {
    const params = new URLSearchParams({
      title: title
    });
    
    const response = await fetch(`${API_BASE}/news/vote?${params}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.count || 0;
  } catch (error) {
    console.error('Error getting vote count:', error);
    return 0;
  }
};

// 获取新闻来源
export const getNewsSources = async () => {
  try {
    const response = await fetch(`${API_BASE}/news/sources`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.sources || [];
  } catch (error) {
    console.error('Error fetching news sources:', error);
    return [];
  }
};

// 获取文章详情
export const getArticleByTitle = async (title) => {
  try {
    const params = new URLSearchParams({
      title: title
    });
    
    const response = await fetch(`${API_BASE}/news/article?${params}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching article:', error);
    throw error;
  }
};

// 生成新闻摘要
export const generateSummary = async (content, summaryType = 'detailed') => {
  try {
    const response = await fetch(`${API_BASE}/news/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: content,
        type: summaryType
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating summary:', error);
    throw error;
  }
};

// 刷新新闻
export const refreshNews = async () => {
  try {
    const response = await fetch(`${API_BASE}/news/refresh`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error refreshing news:', error);
    throw error;
  }
}; 