import { useState, useEffect, useRef } from "react";
import { fetchVote, fetchScore, fetchNewsWithSort } from "../services/api";
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
  const [sortBy, setSortBy] = useState('smart');
  const [sourceFilter, setSourceFilter] = useState('');
  const [showSortMenu, setShowSortMenu] = useState(false);
  const [showSourceMenu, setShowSourceMenu] = useState(false);
  const observerRef = useRef(null);
  const LIMIT = 10;

  // 排序选项
  const sortOptions = [
    { value: 'smart', label: 'Smart Sort' },
    { value: 'time', label: 'Latest' },
    { value: 'popular', label: 'Most Popular' },
    { value: 'ai_quality', label: 'AI Picks' },
    { value: 'source', label: 'By Source' }
  ];

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

  const loadMoreNews = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const data = await fetchNewsWithSort(offset, LIMIT, sortBy, sourceFilter);
      const enriched = await Promise.all(
        data.map(async (item) => {
          const count = await fetchVote(item.title).catch(() => 0);
          const aiScore = await fetchScore(item.content).catch(() => null);
          return { 
            ...item, 
            voteCount: count, 
            aiScore,
            // 使用后端返回的数据
            vote_count: item.vote_count || count,
            ai_score: item.ai_score || aiScore,
            comprehensive_score: item.comprehensive_score
          };
        })
      );
      setNewsList(prevList => [...prevList, ...enriched]);
      setOffset(prev => prev + LIMIT);
    } catch (e) {
      console.error("❌ Failed to load news:", e);
    } finally {
      setLoading(false);
    }
  };

  // 重置新闻列表并重新加载
  const resetAndLoadNews = () => {
    setNewsList([]);
    setOffset(0);
    loadMoreNews();
  };

  // 当排序或筛选条件改变时，重置列表
  useEffect(() => {
    resetAndLoadNews();
  }, [sortBy, sourceFilter]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) loadMoreNews();
      },
      { threshold: 1 }
    );
    if (observerRef.current) observer.observe(observerRef.current);
    return () => observer.disconnect();
  }, [newsList, sortBy, sourceFilter]);

  return (
    <>
      <LoginButton />
      
      {/* 排序和筛选控制栏 */}
      <div style={{
        position: 'fixed',
        top: '4.5rem',
        left: '2rem',
        zIndex: 1000,
        display: 'flex',
        gap: '1rem',
        alignItems: 'center'
      }}>
        {/* 排序选择器 */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowSortMenu(!showSortMenu)}
            style={{
              background: '#fff',
              border: '1px solid #000',
              borderRadius: '4px',
              padding: '0.5rem 1rem',
              fontFamily: 'monospace',
              fontSize: '0.8rem',
              cursor: 'pointer',
              minWidth: '120px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            {sortOptions.find(opt => opt.value === sortBy)?.label || 'Sort'}
            <span>▼</span>
          </button>
          
          {showSortMenu && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              background: '#fff',
              border: '1px solid #000',
              borderRadius: '4px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              zIndex: 1001,
              minWidth: '120px'
            }}>
              {sortOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => {
                    setSortBy(option.value);
                    setShowSortMenu(false);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    fontFamily: 'monospace',
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    width: '100%',
                    textAlign: 'left',
                    color: sortBy === option.value ? '#000' : '#666'
                  }}
                  onMouseEnter={(e) => e.target.style.background = '#f5f5f5'}
                  onMouseLeave={(e) => e.target.style.background = 'none'}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* 来源筛选器 */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowSourceMenu(!showSourceMenu)}
            style={{
              background: '#fff',
              border: '1px solid #000',
              borderRadius: '4px',
              padding: '0.5rem 1rem',
              fontFamily: 'monospace',
              fontSize: '0.8rem',
              cursor: 'pointer',
              minWidth: '140px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            {sourceOptions.find(opt => opt.value === sourceFilter)?.label || 'Source'}
            <span>▼</span>
          </button>
          
          {showSourceMenu && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              background: '#fff',
              border: '1px solid #000',
              borderRadius: '4px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              zIndex: 1001,
              minWidth: '140px',
              maxHeight: '300px',
              overflowY: 'auto'
            }}>
              {sourceOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => {
                    setSourceFilter(option.value);
                    setShowSourceMenu(false);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    fontFamily: 'monospace',
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    width: '100%',
                    textAlign: 'left',
                    color: sourceFilter === option.value ? '#000' : '#666'
                  }}
                  onMouseEnter={(e) => e.target.style.background = '#f5f5f5'}
                  onMouseLeave={(e) => e.target.style.background = 'none'}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 点击外部关闭菜单 */}
      {(showSortMenu || showSourceMenu) && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 999
          }}
          onClick={() => {
            setShowSortMenu(false);
            setShowSourceMenu(false);
          }}
        />
      )}

      <div className="news-container">
        {/* 新闻列表 */}
        {newsList.map((n, idx) => (
          <NewsCard key={n.link + '-' + idx} {...n} />
        ))}

        {/* 加载更多触发器 */}
        <div ref={observerRef} style={{ height: 40 }} />

        {loading && <p style={{ textAlign: "center", marginTop: "1rem" }}>Loading...</p>}
      </div>
    </>
  );
}
