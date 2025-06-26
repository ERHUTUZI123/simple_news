import axios from "axios";

const API_BASE = "https://simplenews-production.up.railway.app";

export function fetchTodayNews(offset = 0, limit = 10) {
  return fetch(`${API_BASE}/news/today?offset=${offset}&limit=${limit}`)
    .then(res => {
      if (!res.ok) throw new Error("API error");
      return res.json();
    });
}

export function fetchSummary(content) {
  return axios
    .post(`${API_BASE}/news/summary`, { content })
    .then(res => res.data.summary);
}

export function voteNews(title, delta = 1) {
  return axios
    .post(`${API_BASE}/news/vote`, null, { params: { title, delta } })
    .then(res => res.data.count);
}

export function downvoteNews(title) {
  return voteNews(title, -1);
}

export function fetchVote(title) {
  return axios
    .get(`${API_BASE}/news/vote`, { params: { title } })
    .then(res => res.data.count);
}

// 获取文章详情
export function fetchArticle(id) {
  return axios
    .get(`${API_BASE}/news/article/${id}`)
    .then(res => res.data);
}

// 根据标题获取文章
export function fetchArticleByTitle(title) {
  return axios
    .get(`${API_BASE}/news/article`, { params: { title } })
    .then(res => res.data);
}

export const fetchNewsWithSort = async (offset = 0, limit = 20, sortBy = 'smart', sourceFilter = null) => {
  try {
    const params = new URLSearchParams({
      offset: offset.toString(),
      limit: limit.toString(),
      sort_by: sortBy
    });
    
    if (sourceFilter) {
      params.append('source_filter', sourceFilter);
    }
    
    const response = await fetch(`${API_BASE}/news/today?${params}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch news');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching news:', error);
    throw error;
  }
};