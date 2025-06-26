import React, { useState, useEffect, useRef } from "react";
import { fetchVote, fetchNewsWithSort } from "../services/api";
import NewsCard, { NewsCardSkeleton } from "../components/NewsCard";
import { GoogleLogin } from '@react-oauth/google';
import { useContext } from "react";
import { UserContext } from "../contexts/UserContext";

function LoginButton() {
  const { userSession, logout } = useContext(UserContext);

  const handleLogout = () => {
    logout();
  };

  return (
    <div style={{
      position: "fixed",
      top: "1rem",
      right: "1rem",
      zIndex: 1001,
      display: "flex",
      alignItems: "center",
      gap: "1rem",
    }}>
      {userSession ? (
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "1rem",
        }}>
          <span style={{
            color: "var(--text-color)",
            fontFamily: "monospace",
            fontSize: "0.9rem",
          }}>
            {userSession.user.name}
          </span>
          <button
            onClick={handleLogout}
            style={{
              background: "none",
              border: "1px solid var(--border-color)",
              borderRadius: "8px",
              padding: "0.5rem 1rem",
              fontFamily: "monospace",
              fontSize: "0.9rem",
              color: "var(--text-color)",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.target.style.opacity = "0.8";
              e.target.style.background = "var(--button-hover-bg)";
            }}
            onMouseLeave={(e) => {
              e.target.style.opacity = "0.7";
              e.target.style.background = "none";
            }}
          >
            logout
          </button>
        </div>
      ) : null}
    </div>
  );
}

export default function Home() {
  const [newsList, setNewsList] = useState([]);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sourceFilter, setSourceFilter] = useState('');
  const [sortBy, setSortBy] = useState('smart'); // 默认智能排序
  const [showSourceMenu, setShowSourceMenu] = useState(false);
  const [showSortMenu, setShowSortMenu] = useState(false);
  const observerRef = useRef(null);
  const LIMIT = 10;

  // 来源选项
  const sourceOptions = [
    { value: '', label: 'All Sources' },
    // 美国主流媒体
    { value: 'The New York Times', label: 'The New York Times' },
    { value: 'The Washington Post', label: 'The Washington Post' },
    { value: 'Los Angeles Times', label: 'Los Angeles Times' },
    { value: 'NBC News', label: 'NBC News' },
    { value: 'CBS News', label: 'CBS News' },
    { value: 'ABC News', label: 'ABC News' },
    { value: 'Fox News', label: 'Fox News' },
    { value: 'CNBC', label: 'CNBC' },
    { value: 'Axios', label: 'Axios' },
    // 国际新闻机构
    { value: 'Reuters', label: 'Reuters' },
    { value: 'Associated Press', label: 'Associated Press' },
    { value: 'Bloomberg', label: 'Bloomberg' },
    // 英国媒体
    { value: 'BBC News', label: 'BBC News' },
    { value: 'The Guardian', label: 'The Guardian' },
    { value: 'The Telegraph', label: 'The Telegraph' },
    { value: 'Financial Times', label: 'Financial Times' },
    { value: 'Sky News', label: 'Sky News' },
    { value: 'The Independent', label: 'The Independent' },
    // 欧洲媒体
    { value: 'Euronews', label: 'Euronews' },
    { value: 'Deutsche Welle', label: 'Deutsche Welle' },
    // 中东媒体
    { value: 'Al Jazeera', label: 'Al Jazeera' },
  ];

  // 排序选项
  const sortOptions = [
    { value: 'smart', label: 'Smart Sort (Recommended)' },
    { value: 'time', label: 'Latest First' },
    { value: 'headlines', label: 'Most Popular' },
  ];

  const getSortLabel = (value) => {
    const option = sortOptions.find(opt => opt.value === value);
    return option ? option.label : 'Smart Sort';
  };

  const getSourceLabel = (value) => {
    const option = sourceOptions.find(opt => opt.value === value);
    return option ? option.label : 'All Sources';
  };

  const resetAndLoadNews = () => {
    setOffset(0);
    setNewsList([]);
    loadMoreNews();
  };

  const loadMoreNews = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const newNews = await fetchNewsWithSort(offset, LIMIT, sortBy, sourceFilter);
      if (offset === 0) {
        setNewsList(newNews);
      } else {
        setNewsList(prev => [...prev, ...newNews]);
      }
      setOffset(prev => prev + LIMIT);
    } catch (error) {
      console.error('Error loading news:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    resetAndLoadNews();
  }, [sortBy, sourceFilter]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loading) {
          loadMoreNews();
        }
      },
      { threshold: 0.1 }
    );

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => observer.disconnect();
  }, [loading, offset, sortBy, sourceFilter]);

  const handleVote = async (title, delta) => {
    try {
      await fetchVote(title, delta);
      // 更新本地新闻列表中的投票数
      setNewsList(prev => prev.map(news => 
        news.title === title 
          ? { ...news, vote_count: (news.vote_count || 0) + delta }
          : news
      ));
    } catch (error) {
      console.error('Error voting:', error);
    }
  };

  return (
    <div className="news-container">
      <LoginButton />
      
      {/* 标题和描述 */}
      <div
        style={{
          textAlign: "center",
          marginBottom: "3rem",
        }}
      >
        <h1 style={{
          fontSize: "3rem",
          fontWeight: "bold",
          marginBottom: "1rem",
        }}>
          OneMinNews
        </h1>
        <p style={{
          fontSize: "1.2rem",
          opacity: 0.9,
          maxWidth: "600px",
          margin: "0 auto",
          lineHeight: "1.6",
        }}>
          AI-powered news aggregation with intelligent sorting
        </p>
      </div>

      {/* 过滤器和排序控件 */}
      <div style={{
        display: "flex",
        justifyContent: "center",
        gap: "1rem",
        marginBottom: "2rem",
        flexWrap: "wrap",
      }}>
        {/* 排序选择器 */}
        <div style={{ position: "relative" }}>
          <button
            onClick={() => setShowSortMenu(!showSortMenu)}
            style={{
              background: "none",
              border: "1px solid var(--border-color)",
              borderRadius: "8px",
              padding: "0.75rem 1rem",
              color: "var(--text-color)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.9rem",
              cursor: "pointer",
              minWidth: "200px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = "var(--button-hover-bg)";
              e.target.style.color = "var(--button-hover-text)";
              e.target.style.borderColor = "var(--button-hover-border)";
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "var(--text-color)";
              e.target.style.borderColor = "var(--border-color)";
            }}
          >
            <span>📊 {getSortLabel(sortBy)}</span>
            <span>▼</span>
          </button>
          
          {showSortMenu && (
            <div style={{
              position: "absolute",
              top: "100%",
              left: 0,
              right: 0,
              background: "var(--bg-color)",
              border: "1px solid var(--border-color)",
              borderRadius: "8px",
              padding: "0.5rem 0",
              marginTop: "0.5rem",
              zIndex: 1000,
            }}>
              {sortOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => {
                    setSortBy(option.value);
                    setShowSortMenu(false);
                  }}
                  style={{
                    width: "100%",
                    padding: "0.5rem 1rem",
                    background: "none",
                    border: "none",
                    textAlign: "left",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.9rem",
                    color: sortBy === option.value ? "var(--highlight-color)" : "var(--text-color)",
                    cursor: "pointer",
                    fontWeight: sortBy === option.value ? "bold" : "normal",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = "var(--button-hover-bg)";
                    e.target.style.color = "var(--button-hover-text)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = "transparent";
                    e.target.style.color = sortBy === option.value ? "var(--highlight-color)" : "var(--text-color)";
                  }}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* 来源过滤器 */}
        <div style={{ position: "relative" }}>
          <button
            onClick={() => setShowSourceMenu(!showSourceMenu)}
            style={{
              background: "none",
              border: "1px solid var(--border-color)",
              borderRadius: "8px",
              padding: "0.75rem 1rem",
              color: "var(--text-color)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.9rem",
              cursor: "pointer",
              minWidth: "200px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = "var(--button-hover-bg)";
              e.target.style.color = "var(--button-hover-text)";
              e.target.style.borderColor = "var(--button-hover-border)";
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "var(--text-color)";
              e.target.style.borderColor = "var(--border-color)";
            }}
          >
            <span>📰 {getSourceLabel(sourceFilter)}</span>
            <span>▼</span>
          </button>
          
          {showSourceMenu && (
            <div style={{
              position: "absolute",
              top: "100%",
              left: 0,
              right: 0,
              background: "var(--bg-color)",
              border: "1px solid var(--border-color)",
              borderRadius: "8px",
              padding: "0.5rem 0",
              marginTop: "0.5rem",
              zIndex: 1000,
              maxHeight: "300px",
              overflowY: "auto",
            }}>
              {sourceOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => {
                    setSourceFilter(option.value);
                    setShowSourceMenu(false);
                  }}
                  style={{
                    width: "100%",
                    padding: "0.5rem 1rem",
                    background: "none",
                    border: "none",
                    textAlign: "left",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.9rem",
                    color: sourceFilter === option.value ? "var(--highlight-color)" : "var(--text-color)",
                    cursor: "pointer",
                    fontWeight: sourceFilter === option.value ? "bold" : "normal",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = "var(--button-hover-bg)";
                    e.target.style.color = "var(--button-hover-text)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = "transparent";
                    e.target.style.color = sourceFilter === option.value ? "var(--highlight-color)" : "var(--text-color)";
                  }}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 新闻列表 */}
      <div className="news-list">
        {loading && newsList.length === 0 ? (
          // 加载中且无数据时显示骨架屏
          Array.from({ length: 5 }).map((_, i) => <NewsCardSkeleton key={i} />)
        ) : (
          newsList.map((news, index) => (
            <div key={`${news.title}-${index}`}>
              <NewsCard
                news={news}
                onVote={handleVote}
                showScore={sortBy === 'smart'}
              />
            </div>
          ))
        )}
        {loading && newsList.length > 0 && (
          <div style={{ textAlign: "center", padding: "2rem", color: "var(--secondary-color)", fontFamily: "var(--font-mono)" }}>
            Loading more news...
          </div>
        )}
        <div ref={observerRef} style={{ height: "20px" }} />
      </div>
    </div>
  );
}
