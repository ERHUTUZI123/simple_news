import { useState, useEffect, useRef } from "react";
import { fetchVote, fetchNewsWithSort } from "../services/api";
import NewsCard from "../components/NewsCard";
import { GoogleLogin } from '@react-oauth/google';

// 解析JWT token获取用户信息
function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error parsing JWT:', error);
    return null;
  }
}

function LoginButton() {
  const [showGoogleLogin, setShowGoogleLogin] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("id_token");
    if (token) {
      const parsed = parseJwt(token);
      if (parsed) {
        setUserInfo(parsed);
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("id_token");
    setUserInfo(null);
    window.location.reload();
  };

  const handleLoginSuccess = (credentialResponse) => {
    localStorage.setItem("id_token", credentialResponse.credential);
    const parsed = parseJwt(credentialResponse.credential);
    if (parsed) {
      setUserInfo(parsed);
    }
    setShowGoogleLogin(false);
    window.location.reload();
  };

  return (
    <div style={{
      position: "fixed",
      top: "4.5rem",
      right: 32,
      zIndex: 1000,
    }}>
      {userInfo ? (
        // 已登录状态：显示用户ID
        <div style={{
          background: "transparent",
          border: "none",
          padding: "0.5rem 1rem",
          fontFamily: "monospace",
          fontSize: "0.9rem",
          color: "#fff",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
        }}>
          <span>{userInfo.email || userInfo.name || 'User'}</span>
          <button
            onClick={handleLogout}
            style={{
              background: "none",
              border: "none",
              color: "#fff",
              fontFamily: "monospace",
              fontSize: "0.8rem",
              cursor: "pointer",
              opacity: 0.7,
              padding: "0.2rem 0.5rem",
              borderRadius: "4px",
            }}
            onMouseEnter={(e) => {
              e.target.style.opacity = "1";
              e.target.style.background = "rgba(255,255,255,0.1)";
            }}
            onMouseLeave={(e) => {
              e.target.style.opacity = "0.7";
              e.target.style.background = "none";
            }}
          >
            logout
          </button>
        </div>
      ) : !showGoogleLogin ? (
        // 未登录状态：显示Sign in按钮
        <button
          onClick={() => setShowGoogleLogin(true)}
          style={{
            background: "#fff",
            border: "1px solid #000",
            borderRadius: "8px",
            padding: "0.5rem 1rem",
            fontFamily: "monospace",
            fontSize: "0.9rem",
            color: "#000",
            cursor: "pointer",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.target.style.background = "#f5f5f5";
            e.target.style.transform = "translateY(-1px)";
          }}
          onMouseLeave={(e) => {
            e.target.style.background = "#fff";
            e.target.style.transform = "translateY(0)";
          }}
        >
          Sign in
        </button>
      ) : (
        // 显示Google登录弹窗
        <div style={{
          background: "#fff",
          border: "1px solid #000",
          borderRadius: "8px",
          padding: "1rem",
          boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
          minWidth: "200px",
        }}>
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "0.5rem",
          }}>
            <span style={{
              fontFamily: "monospace",
              fontSize: "0.9rem",
              color: "#000",
            }}>
              Sign in with Google
            </span>
            <button
              onClick={() => setShowGoogleLogin(false)}
              style={{
                background: "none",
                border: "none",
                fontSize: "1.2rem",
                cursor: "pointer",
                color: "#666",
                padding: "0",
                width: "20px",
                height: "20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              ×
            </button>
          </div>
          <GoogleLogin
            onSuccess={handleLoginSuccess}
            onError={() => {
              alert("Google login failed");
            }}
            theme="outline"
            size="medium"
            width="100%"
            text="signin_with"
            shape="rectangular"
          />
        </div>
      )}
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

  // 来源选项
  const sourceOptions = [
    { value: '', label: 'All Sources' },
    { value: 'Financial Times', label: 'Financial Times' },
    { value: 'Wall Street Journal', label: 'Wall Street Journal' },
    { value: 'The Economist', label: 'The Economist' },
    { value: 'Reuters', label: 'Reuters' },
    { value: 'Bloomberg', label: 'Bloomberg' },
    { value: 'BBC', label: 'BBC' },
    { value: 'CNN', label: 'CNN' },
    { value: 'The New York Times', label: 'The New York Times' },
    { value: 'TechCrunch', label: 'TechCrunch' },
    { value: 'Ars Technica', label: 'Ars Technica' },
    { value: 'Wired', label: 'Wired' }
  ];

  // Reset news list and reload
  const resetAndLoadNews = () => {
    setNewsList([]);
    setOffset(0);
    loadMoreNews();
  };

  // Load more news
  const loadMoreNews = async () => {
    if (loading) return;
    
    setLoading(true);
    try {
      const news = await fetchNewsWithSort(offset, LIMIT, 'time', sourceFilter);
      if (news && news.length > 0) {
        setNewsList(prev => [...prev, ...news]);
        setOffset(prev => prev + LIMIT);
      }
    } catch (error) {
      console.error('Failed to load news:', error);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    resetAndLoadNews();
  }, [sourceFilter]);

  // Infinite scroll
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
  }, [loading, offset]);

  return (
    <div className="news-container">
      <LoginButton />
      
      {/* Source filter */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        marginBottom: '2rem',
        position: 'relative',
      }}>
        <div style={{
          position: 'relative',
          display: 'inline-block',
        }}>
          <button
            onClick={() => setShowSourceMenu(!showSourceMenu)}
            style={{
              background: 'none',
              border: '1px solid var(--border-color)',
              color: 'var(--text-color)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.9rem',
              cursor: 'pointer',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.25rem',
              transition: 'all 0.2s ease',
              display: 'flex',
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
            📰 {sourceFilter || 'All Sources'} {showSourceMenu ? '▲' : '▼'}
          </button>

          {showSourceMenu && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              background: 'var(--bg-color)',
              border: '1px solid var(--border-color)',
              borderRadius: '0.25rem',
              marginTop: '0.25rem',
              zIndex: 1000,
              maxHeight: '300px',
              overflowY: 'auto',
            }}>
              {sourceOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => {
                    setSourceFilter(option.value);
                    setShowSourceMenu(false);
                  }}
                  style={{
                    width: '100%',
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-color)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    padding: '0.75rem 1rem',
                    textAlign: 'left',
                    transition: 'all 0.2s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = 'transparent';
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
      <div className="news-list">
        {newsList.map((news, index) => (
          <NewsCard
            key={`${news.title}-${index}`}
            title={news.title}
            link={news.link}
            date={news.date}
            source={news.source}
            content={news.content}
            comprehensive_score={news.comprehensive_score}
            vote_count={news.vote_count}
          />
        ))}
      </div>

      {/* Loading indicator */}
      {loading && (
        <div style={{
          textAlign: 'center',
          padding: '2rem',
          color: 'var(--secondary-color)',
          fontFamily: 'var(--font-mono)',
        }}>
          Loading more news...
        </div>
      )}

      {/* Observer for infinite scroll */}
      <div ref={observerRef} style={{ height: '1px' }} />
    </div>
  );
}
