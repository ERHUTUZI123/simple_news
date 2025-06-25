import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchSummary, fetchArticleByTitle } from '../services/api';

// 格式化相对时间
function formatRelativeTime(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMin = Math.floor(diffMs / 1000 / 60);
  if (diffMin < 60) {
    return `${diffMin <= 0 ? 1 : diffMin}m`;
  }
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) {
    return `${diffH}h`;
  }
  const diffD = Math.floor(diffH / 24);
  return `${diffD}d`;
}

// 简单去除 HTML 标签
function stripHtml(html) {
  const tmp = document.createElement("div");
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || "";
}

export default function Article() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [summaryType, setSummaryType] = useState('detailed'); // 'brief' or 'detailed'

  // 检查文章是否已收藏
  useEffect(() => {
    if (article) {
      const saved = localStorage.getItem('savedArticles') || '[]';
      const savedArticles = JSON.parse(saved);
      const isArticleSaved = savedArticles.some(savedArticle => savedArticle.title === article.title);
      setIsSaved(isArticleSaved);
    }
  }, [article]);

  // 从API获取文章数据
  useEffect(() => {
    const loadArticle = async () => {
      try {
        setLoading(true);
        // 解码URL参数
        const decodedId = decodeURIComponent(id);
        
        // 尝试从API获取文章数据
        const articleData = await fetchArticleByTitle(decodedId);
        setArticle(articleData);
      } catch (error) {
        console.error('Failed to load article:', error);
        // 如果API失败，使用模拟数据
        const decodedId = decodeURIComponent(id);
        const mockArticle = {
          id: id,
          title: decodedId || "Sample Article Title - This is a long title that might wrap to two lines",
          source: "BBC",
          date: new Date().toISOString(),
          link: "https://www.bbc.com/news/article",
          content: "This is a sample article content that would be used to generate AI summary..."
        };
        setArticle(mockArticle);
      } finally {
        setLoading(false);
      }
    };

    loadArticle();
  }, [id]);

  // 生成AI摘要
  const generateSummary = async () => {
    if (!article) return;
    
    setSummaryLoading(true);
    try {
      const key = `summary-${article.id}-${summaryType}`;
      const cached = localStorage.getItem(key);
      
      if (cached) {
        setSummary(stripHtml(cached));
      } else {
        const result = await fetchSummary(article.content);
        localStorage.setItem(key, result);
        setSummary(stripHtml(result));
      }
    } catch (error) {
      console.error('Failed to generate summary:', error);
      setSummary("Failed to generate summary. Please try again.");
    } finally {
      setSummaryLoading(false);
    }
  };

  // 切换摘要类型
  const toggleSummaryType = () => {
    setSummaryType(summaryType === 'detailed' ? 'brief' : 'detailed');
    setSummary(''); // 清空当前摘要，重新生成
  };

  // 收藏功能
  const toggleSaved = () => {
    if (!article) return;
    
    const saved = localStorage.getItem('savedArticles') || '[]';
    const savedArticles = JSON.parse(saved);
    
    if (isSaved) {
      // 移除收藏
      const updatedArticles = savedArticles.filter(savedArticle => savedArticle.title !== article.title);
      localStorage.setItem('savedArticles', JSON.stringify(updatedArticles));
      setIsSaved(false);
    } else {
      // 添加收藏
      const articleToSave = {
        title: article.title,
        link: article.link,
        date: article.date,
        source: article.source,
        content: article.content,
        summary: summary || ""
      };
      const updatedArticles = [...savedArticles, articleToSave];
      localStorage.setItem('savedArticles', JSON.stringify(updatedArticles));
      setIsSaved(true);
    }
  };

  // 分享功能
  const shareArticle = async () => {
    try {
      await navigator.share({
        title: article?.title,
        text: `Check out this article: ${article?.title}`,
        url: window.location.href,
      });
    } catch (_error) {
      console.log('Native sharing not supported, copying to clipboard');
      // 如果不支持原生分享，复制链接
      navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        fontFamily: 'var(--font-mono)',
        color: 'var(--text-color)',
      }}>
        Loading...
      </div>
    );
  }

  if (!article) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        fontFamily: 'var(--font-mono)',
        color: 'var(--text-color)',
      }}>
        Article not found
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-color)',
      color: 'var(--text-color)',
      fontFamily: 'var(--font-mono)',
    }}>
      {/* 顶部导航 */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: '3.5rem',
        background: 'var(--bg-color)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 2rem',
        zIndex: 1000,
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '2rem',
        }}>
          <span style={{
            fontWeight: '600',
            fontSize: '1rem',
            letterSpacing: '0.05em',
          }}>
            ONEMINEWS
          </span>
        </div>
        
        <button
          onClick={() => navigate('/')}
          style={{
            background: 'none',
            border: '1px solid var(--border-color)',
            color: 'var(--text-color)',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.9rem',
            cursor: 'pointer',
            padding: '0.5rem 1rem',
            borderRadius: '0.25rem',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = 'var(--text-color)';
            e.target.style.color = 'var(--bg-color)';
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'transparent';
            e.target.style.color = 'var(--text-color)';
          }}
        >
          ← Back to Home
        </button>
      </div>

      {/* 主要内容 */}
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        padding: '5rem 2rem 2rem',
        lineHeight: '1.6',
      }}>
        {/* 文章信息 */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{
            fontSize: '0.9rem',
            color: 'var(--secondary-color)',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}>
            <span>📰</span>
            <span>{article.source}</span>
            <span>·</span>
            <span>🕒</span>
            <span>{formatRelativeTime(article.date)}</span>
          </div>

          <h1 style={{
            fontSize: '1.8rem',
            fontWeight: '700',
            marginBottom: '2rem',
            lineHeight: '1.3',
            color: 'var(--text-color)',
          }}>
            # {article.title}
          </h1>
        </div>

        {/* 摘要类型切换 */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          marginBottom: '2rem',
        }}>
          <button
            onClick={toggleSummaryType}
            style={{
              background: 'none',
              border: '1px solid var(--border-color)',
              color: 'var(--text-color)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.9rem',
              cursor: 'pointer',
              padding: '0.5rem 1rem',
              borderRadius: '0.25rem',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = 'var(--text-color)';
              e.target.style.color = 'var(--bg-color)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'transparent';
              e.target.style.color = 'var(--text-color)';
            }}
          >
            {summaryType === 'detailed' ? '📝 Detailed' : '📋 Brief'}
          </button>

          {!summary && (
            <button
              onClick={generateSummary}
              disabled={summaryLoading}
              style={{
                background: 'var(--highlight-color)',
                border: 'none',
                color: 'var(--bg-color)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.9rem',
                cursor: summaryLoading ? 'not-allowed' : 'pointer',
                padding: '0.5rem 1rem',
                borderRadius: '0.25rem',
                transition: 'all 0.2s ease',
                opacity: summaryLoading ? 0.6 : 1,
              }}
            >
              {summaryLoading ? 'Generating...' : '🤖 Generate AI Summary'}
            </button>
          )}
        </div>

        {/* AI 摘要内容 */}
        {summary && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-color)',
            borderRadius: '0.5rem',
            padding: '2rem',
            marginBottom: '2rem',
            animation: 'fadeIn 0.4s ease-in-out',
          }}>
            <h2 style={{
              fontSize: '1.2rem',
              fontWeight: '600',
              marginBottom: '1rem',
              color: 'var(--highlight-color)',
            }}>
              --- AI Summary ({summaryType === 'detailed' ? 'Detailed' : 'Brief'}) ---
            </h2>
            
            <div style={{
              fontSize: '1rem',
              lineHeight: '1.7',
              color: 'var(--text-color)',
              whiteSpace: 'pre-wrap',
            }}>
              {summary}
            </div>
          </div>
        )}

        {/* 辅助功能区 */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '1rem',
          padding: '1.5rem',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-color)',
          borderRadius: '0.5rem',
        }}>
          <a
            href={article.link}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: 'var(--text-color)',
              textDecoration: 'none',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.9rem',
              padding: '0.5rem 1rem',
              border: '1px solid var(--border-color)',
              borderRadius: '0.25rem',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = 'var(--text-color)';
              e.target.style.color = 'var(--bg-color)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'transparent';
              e.target.style.color = 'var(--text-color)';
            }}
          >
            🔗 Original Article
          </a>

          <button
            onClick={toggleSaved}
            style={{
              background: 'none',
              border: '1px solid var(--border-color)',
              color: isSaved ? 'var(--highlight-color)' : 'var(--text-color)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.9rem',
              cursor: 'pointer',
              padding: '0.5rem 1rem',
              borderRadius: '0.25rem',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
            onMouseEnter={(e) => {
              if (!isSaved) {
                e.target.style.backgroundColor = 'var(--text-color)';
                e.target.style.color = 'var(--bg-color)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isSaved) {
                e.target.style.backgroundColor = 'transparent';
                e.target.style.color = 'var(--text-color)';
              }
            }}
          >
            {isSaved ? '⭐ Saved' : '⭐ Save'}
          </button>

          <button
            onClick={shareArticle}
            style={{
              background: 'none',
              border: '1px solid var(--border-color)',
              color: 'var(--text-color)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.9rem',
              cursor: 'pointer',
              padding: '0.5rem 1rem',
              borderRadius: '0.25rem',
              transition: 'all 0.2s ease',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = 'var(--text-color)';
              e.target.style.color = 'var(--bg-color)';
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'transparent';
              e.target.style.color = 'var(--text-color)';
            }}
          >
            🔗 Share
          </button>
        </div>
      </div>
    </div>
  );
} 