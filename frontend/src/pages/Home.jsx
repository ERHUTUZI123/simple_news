import React, { useState, useEffect, useRef } from "react";
import { fetchNewsWithSort, voteNews } from "../services/api";
import NewsCard from "../components/NewsCard";
import PageTitle from "../components/PageTitle";
import { useContext } from "react";
import { UserContext } from "../context/UserContext";
import { GoogleLogin } from '@react-oauth/google';

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
  const [showSourceMenu, setShowSourceMenu] = useState(false);
  const observerRef = useRef(null);
  const LIMIT = 10;

  // Source options
  const sourceOptions = [
    { value: '', label: 'All Sources' },
    // American mainstream media
    { value: 'The New York Times', label: 'The New York Times' },
    { value: 'The Washington Post', label: 'The Washington Post' },
    { value: 'Los Angeles Times', label: 'Los Angeles Times' },
    { value: 'NBC News', label: 'NBC News' },
    { value: 'CBS News', label: 'CBS News' },
    { value: 'ABC News', label: 'ABC News' },
    { value: 'Fox News', label: 'Fox News' },
    { value: 'CNBC', label: 'CNBC' },
    { value: 'Axios', label: 'Axios' },
    // International news agencies
    { value: 'Reuters', label: 'Reuters' },
    { value: 'Associated Press', label: 'Associated Press' },
    { value: 'Bloomberg', label: 'Bloomberg' },
    // British media
    { value: 'BBC News', label: 'BBC News' },
    { value: 'The Guardian', label: 'The Guardian' },
    { value: 'The Telegraph', label: 'The Telegraph' },
    { value: 'Financial Times', label: 'Financial Times' },
    { value: 'Sky News', label: 'Sky News' },
    { value: 'The Independent', label: 'The Independent' },
    // European media
    { value: 'Euronews', label: 'Euronews' },
    { value: 'Deutsche Welle', label: 'Deutsche Welle' },
    // Middle Eastern media
    { value: 'Al Jazeera', label: 'Al Jazeera' },
  ];

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
      const newNews = await fetchNewsWithSort(offset, LIMIT, sourceFilter);
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
  }, [sourceFilter]);

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
  }, [loading, offset, sourceFilter]);

  const handleVote = async (title, delta) => {
    try {
      await voteNews(title, delta);
      // Reload news to update vote count
      resetAndLoadNews();
    } catch (error) {
      console.error('Error voting:', error);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <LoginButton />
      
      {/* Title and description */}
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

      {/* Filter area */}
      <div style={{
        marginBottom: "2rem",
        display: "flex",
        gap: "1rem",
        flexWrap: "wrap",
      }}>
        {/* Source filter */}
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

      {/* News list */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {newsList.map((news, index) => (
          <div key={`${news.id}-${index}`}>
            <NewsCard
              news={news}
              onVote={handleVote}
            />
          </div>
        ))}
      </div>

      {/* Load more indicator */}
      {loading && (
        <div style={{
          textAlign: "center",
          padding: "2rem",
          color: "var(--text-secondary)",
          fontFamily: "var(--font-mono)",
        }}>
          Loading more news...
        </div>
      )}

      {/* Infinite scroll observer */}
      <div ref={observerRef} style={{ height: "20px" }} />
    </div>
  );
}
