const API_BASE = "https://simplenews-production.up.railway.app";

// Get news list (only supports time sorting)
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

// Vote functionality
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

// Downvote (compatibility function)
export const downvoteNews = async (title) => {
  return voteNews(title, -1);
};

// Get vote count
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

// Get news sources
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

// Get article details
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

// Compatibility function alias
export const fetchArticleByTitle = getArticleByTitle;

// Generate news summary
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

// Compatibility function alias
export const fetchSummary = async (content, type = 'detailed') => {
  const result = await generateSummary(content, type);
  return result.summary || result;
};

// Refresh news
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