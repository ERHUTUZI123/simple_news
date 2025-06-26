import { useState, useEffect, useRef } from "react";
import { fetchVote, fetchNewsWithSort } from "../services/api";
import NewsCard from "../components/NewsCard";
import { GoogleLogin } from '@react-oauth/google';
import { motion } from 'framer-motion';

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
  const [sortBy, setSortBy] = useState('smart'); // 默认智能排序
  const [showSourceMenu, setShowSourceMenu] = useState(false);
  const [showSortMenu, setShowSortMenu] = useState(false);
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
    { value: 'AP', label: 'Associated Press' },
    { value: 'BBC', label: 'BBC' },
    { value: 'CNN', label: 'CNN' },
    { value: 'The Guardian', label: 'The Guardian' },
    { value: 'TechCrunch', label: 'TechCrunch' },
    { value: 'Ars Technica', label: 'Ars Technica' },
    { value: 'Wired', label: 'Wired' },
    { value: 'The Verge', label: 'The Verge' },
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
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      padding: "2rem 1rem",
      fontFamily: "monospace",
    }}>
      <LoginButton />
      
      {/* 标题和描述 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        style={{
          textAlign: "center",
          marginBottom: "3rem",
          color: "#fff",
        }}
      >
        <h1 style={{
          fontSize: "3rem",
          fontWeight: "bold",
          marginBottom: "1rem",
          textShadow: "0 2px 4px rgba(0,0,0,0.3)",
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
      </motion.div>

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
              background: "rgba(255,255,255,0.1)",
              border: "1px solid rgba(255,255,255,0.3)",
              borderRadius: "8px",
              padding: "0.75rem 1rem",
              color: "#fff",
              fontFamily: "monospace",
              fontSize: "0.9rem",
              cursor: "pointer",
              backdropFilter: "blur(10px)",
              minWidth: "200px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
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
              background: "rgba(255,255,255,0.95)",
              border: "1px solid rgba(0,0,0,0.1)",
              borderRadius: "8px",
              padding: "0.5rem 0",
              marginTop: "0.5rem",
              backdropFilter: "blur(10px)",
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
                    fontFamily: "monospace",
                    fontSize: "0.9rem",
                    color: sortBy === option.value ? "#667eea" : "#333",
                    cursor: "pointer",
                    fontWeight: sortBy === option.value ? "bold" : "normal",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = "rgba(102, 126, 234, 0.1)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = "none";
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
              background: "rgba(255,255,255,0.1)",
              border: "1px solid rgba(255,255,255,0.3)",
              borderRadius: "8px",
              padding: "0.75rem 1rem",
              color: "#fff",
              fontFamily: "monospace",
              fontSize: "0.9rem",
              cursor: "pointer",
              backdropFilter: "blur(10px)",
              minWidth: "200px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
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
              background: "rgba(255,255,255,0.95)",
              border: "1px solid rgba(0,0,0,0.1)",
              borderRadius: "8px",
              padding: "0.5rem 0",
              marginTop: "0.5rem",
              backdropFilter: "blur(10px)",
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
                    fontFamily: "monospace",
                    fontSize: "0.9rem",
                    color: sourceFilter === option.value ? "#667eea" : "#333",
                    cursor: "pointer",
                    fontWeight: sourceFilter === option.value ? "bold" : "normal",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = "rgba(102, 126, 234, 0.1)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = "none";
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
      <div style={{
        maxWidth: "800px",
        margin: "0 auto",
        display: "flex",
        flexDirection: "column",
        gap: "1.5rem",
      }}>
        {newsList.map((news, index) => (
          <motion.div
            key={`${news.title}-${index}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <NewsCard
              news={news}
              onVote={handleVote}
              showScore={sortBy === 'smart'} // 智能排序时显示评分
            />
          </motion.div>
        ))}
        
        {loading && (
          <div style={{
            textAlign: "center",
            padding: "2rem",
            color: "#fff",
            fontFamily: "monospace",
          }}>
            Loading more news...
          </div>
        )}
        
        <div ref={observerRef} style={{ height: "20px" }} />
      </div>
    </div>
  );
}
