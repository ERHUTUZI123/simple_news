import React, { useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import {
  voteNews,
  downvoteNews,
} from "../services/api";
import { UserContext } from "../context/UserContext";
import { toast } from "react-toastify";

// 格式化相对时间（展示分钟 m、小时 h、天 d）
function formatRelativeTime(dateString) {
  if (!dateString) {
    console.log("No date string provided");
    return "unknown";
  }
  
  console.log("Formatting date:", dateString, "Type:", typeof dateString);
  
  try {
    const date = new Date(dateString);
    console.log("Parsed date:", date, "Valid:", !isNaN(date.getTime()));
    
    if (isNaN(date.getTime())) {
      console.log("Invalid date:", dateString);
      return "invalid date";
    }
    
    const now = new Date();
    const diffMs = now - date;
    const diffMin = Math.floor(diffMs / (1000 * 60));
    
    console.log("Time calculation:", {
      date: date.toISOString(),
      now: now.toISOString(),
      diffMs,
      diffMin
    });
    
    if (diffMin < 1) {
      return "now";
    }
    if (diffMin < 60) {
      return `${diffMin}m`;
    }
    
    const diffH = Math.floor(diffMin / 60);
    if (diffH < 24) {
      return `${diffH}h`;
    }
    
    const diffD = Math.floor(diffH / 24);
    return `${diffD}d`;
  } catch (error) {
    console.error("Error formatting date:", error);
    return "error";
  }
}

// 安全格式化关键词
function formatKeywords(keywords) {
  try {
    if (!keywords) return "";
    
    // 如果是字符串，尝试解析为JSON
    if (typeof keywords === 'string') {
      try {
        const parsed = JSON.parse(keywords);
        if (Array.isArray(parsed)) {
          return parsed.slice(0, 3).join(", ");
        }
      } catch (e) {
        // 如果解析失败，直接返回字符串
        return keywords;
      }
    }
    
    // 如果是数组
    if (Array.isArray(keywords)) {
      return keywords.slice(0, 3).join(", ");
    }
    
    // 其他情况，转换为字符串
    return String(keywords);
  } catch (error) {
    console.error("Error formatting keywords:", error);
    return "";
  }
}

export default function NewsCard({ news, onVote, showScore = false }) {
  const navigate = useNavigate();
  const userSession = useContext(UserContext);
  const [isSaved, setIsSaved] = useState(false);
  const [isHeadline, setIsHeadline] = useState(false);
  const [isTrash, setIsTrash] = useState(false);

  // 从news对象中提取数据
  const { id, title, link, date, source, content, score, vote_count, keywords } = news;

  // Check if article is bookmarked
  useEffect(() => {
    const checkSavedStatus = async () => {
      if (!userSession) {
        setIsSaved(false);
        return;
      }
      
      try {
        const response = await fetch(`/api/saved/check?user_id=${userSession.user.id}&news_id=${encodeURIComponent(title)}`);
        if (response.ok) {
          const data = await response.json();
          setIsSaved(data.saved);
        } else {
          setIsSaved(false);
        }
      } catch (error) {
        console.error("Error checking saved status:", error);
        setIsSaved(false);
      }
    };
    
    checkSavedStatus();
  }, [title, userSession]);

  // Like or undo
  const toggleHeadline = async () => {
    if (isHeadline) {
      setIsHeadline(false);
      await downvoteNews(title);
      if (onVote) onVote(title, -1);
    } else {
      setIsHeadline(true);
      setIsTrash(false);
      await voteNews(title);
      if (onVote) onVote(title, 1);
    }
  };

  // Trash or undo
  const toggleTrash = async () => {
    if (isTrash) {
      setIsTrash(false);
      await voteNews(title);
      if (onVote) onVote(title, 1);
    } else {
      setIsTrash(true);
      setIsHeadline(false);
      await downvoteNews(title);
      if (onVote) onVote(title, -1);
    }
  };

  // Bookmark function
  const onSaveClick = async () => {
    if (!userSession) {
      toast("Please login with Google to save articles.");
      if (window.triggerGoogleLogin) window.triggerGoogleLogin();
      return;
    }
    
    try {
      if (isSaved) {
        // 取消保存
        const response = await fetch("/api/save", {
          method: "DELETE",
          body: JSON.stringify({ 
            newsId: title, 
            userId: userSession.user.id 
          }),
          headers: { "Content-Type": "application/json" }
        });
        
        if (response.ok) {
          setIsSaved(false);
          toast("Article removed from saved");
        } else {
          const error = await response.json();
          toast(`Failed to remove article: ${error.detail}`);
        }
      } else {
        // 保存文章
        const response = await fetch("/api/save", {
          method: "POST",
          body: JSON.stringify({ 
            newsId: title, 
            userId: userSession.user.id 
          }),
          headers: { "Content-Type": "application/json" }
        });
        
        if (response.ok) {
          setIsSaved(true);
          toast("Article saved successfully!");
        } else {
          const error = await response.json();
          toast(`Failed to save article: ${error.detail}`);
        }
      }
    } catch (error) {
      console.error("Save operation failed:", error);
      toast("Failed to save article. Please try again.");
    }
  };

  // Jump to Article page
  const goToArticle = () => {
    // Use title as slug, in actual projects should use unique ID
    const slug = encodeURIComponent(title);
    navigate(`/article/${slug}`);
  };

  return (
    <div className={`news-card${isHeadline ? " headline" : ""}${isTrash ? " trash" : ""}`}>
      {/* 来源和时间 */}
      <div className="meta">
        <span style={{ color: "var(--highlight-color)" }}>✅</span> {source} 
        <span style={{ margin: "0 0.5rem" }}>🕒</span> {formatRelativeTime(date)}
        
        {/* 评分信息 */}
        {vote_count > 0 && (
          <span style={{ margin: "0 0.5rem", color: "var(--highlight-color)" }}>
            👍 {vote_count}
          </span>
        )}
        
        {/* 智能评分显示 */}
        {showScore && score && (
          <span style={{ 
            margin: "0 0.5rem", 
            color: score > 0.7 ? "#4CAF50" : score > 0.4 ? "#FF9800" : "#F44336",
            fontSize: "0.8rem",
            fontWeight: "bold"
          }}>
            ⭐ {Math.round(score * 100)}%
          </span>
        )}
        
        {/* 关键词显示 */}
        {keywords && (
          <span style={{ 
            margin: "0 0.5rem", 
            color: "var(--text-color)", 
            fontSize: "0.7rem",
            opacity: 0.7
          }}>
            🏷️ {formatKeywords(keywords)}
          </span>
        )}
      </div>

      {/* 标题 */}
      <h3 className="title">
        <a href={link} target="_blank" rel="noopener noreferrer">
          # {title}
        </a>
        {isHeadline && <span className="badge">HEADLINE</span>}
      </h3>

      {/* 操作按钮 */}
      <div className="actions">
        <button
          onClick={goToArticle}
          style={{
            background: "var(--show-summary-bg)",
            border: "1px solid var(--border-color)",
            color: "var(--show-summary-text)",
            fontFamily: "var(--font-mono)",
            fontSize: "0.9rem",
            cursor: "pointer",
            padding: "0.5rem 1rem",
            borderRadius: "0.25rem",
            transition: "all 0.2s ease",
            display: "inline-block",
            marginRight: "1rem",
          }}
          onMouseEnter={(e) => {
            e.target.style.opacity = "0.8";
            e.target.style.transform = "translateY(-1px)";
          }}
          onMouseLeave={(e) => {
            e.target.style.opacity = "1";
            e.target.style.transform = "translateY(0)";
          }}
        >
          📖 Read Summary
        </button>

        <a 
          href={link} 
          target="_blank" 
          rel="noopener noreferrer"
          style={{
            color: "var(--text-color)",
            textDecoration: "none",
            fontFamily: "var(--font-mono)",
            fontSize: "0.9rem",
            padding: "0.5rem 1rem",
            border: "1px solid var(--border-color)",
            borderRadius: "0.25rem",
            transition: "all 0.2s ease",
            display: "inline-block",
            marginRight: "1rem",
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
          View Original
        </a>

        <button
          onClick={onSaveClick}
          style={{
            background: isSaved ? "var(--highlight-color)" : "none",
            border: "1px solid var(--border-color)",
            color: isSaved ? "white" : "var(--text-color)",
            fontFamily: "var(--font-mono)",
            fontSize: "0.9rem",
            cursor: "pointer",
            padding: "0.5rem 1rem",
            borderRadius: "0.25rem",
            transition: "all 0.2s ease",
            marginRight: "1rem",
          }}
          onMouseEnter={e => {
            if (!isSaved) {
              e.target.style.backgroundColor = "var(--like-hover-bg)";
              e.target.style.color = "var(--like-hover-text)";
              e.target.style.borderColor = "var(--like-hover-border)";
            }
          }}
          onMouseLeave={e => {
            if (!isSaved) {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "var(--text-color)";
              e.target.style.borderColor = "var(--border-color)";
            }
          }}
        >
          {isSaved ? "⭐ Saved" : "⭐ Save"}
        </button>

        <button
          onClick={toggleHeadline}
          style={{
            background: isHeadline ? "var(--highlight-color)" : "none",
            border: "1px solid var(--border-color)",
            color: isHeadline ? "white" : "var(--text-color)",
            fontFamily: "var(--font-mono)",
            fontSize: "0.9rem",
            cursor: "pointer",
            padding: "0.5rem 1rem",
            borderRadius: "0.25rem",
            transition: "all 0.2s ease",
            marginRight: "1rem",
          }}
          onMouseEnter={(e) => {
            if (!isHeadline) {
              e.target.style.backgroundColor = "var(--like-hover-bg)";
              e.target.style.color = "var(--like-hover-text)";
              e.target.style.borderColor = "var(--like-hover-border)";
            }
          }}
          onMouseLeave={(e) => {
            if (!isHeadline) {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "var(--text-color)";
              e.target.style.borderColor = "var(--border-color)";
            }
          }}
        >
          {isHeadline ? "👍 Liked" : "👍 Like"}
        </button>

        <button
          onClick={toggleTrash}
          style={{
            background: isTrash ? "#f44336" : "none",
            border: "1px solid var(--border-color)",
            color: isTrash ? "white" : "var(--text-color)",
            fontFamily: "var(--font-mono)",
            fontSize: "0.9rem",
            cursor: "pointer",
            padding: "0.5rem 1rem",
            borderRadius: "0.25rem",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            if (!isTrash) {
              e.target.style.backgroundColor = "var(--trash-hover-bg)";
              e.target.style.color = "var(--trash-hover-text)";
              e.target.style.borderColor = "var(--trash-hover-border)";
            }
          }}
          onMouseLeave={(e) => {
            if (!isTrash) {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "var(--text-color)";
              e.target.style.borderColor = "var(--border-color)";
            }
          }}
        >
          {isTrash ? "🗑️ Trashed" : "🗑️ Trash"}
        </button>
      </div>
    </div>
  );
}

// 骨架屏组件
export function NewsCardSkeleton() {
  return (
    <div className="news-card skeleton">
      <div className="skeleton-title" style={{width: '70%', height: 24, background: '#eee', marginBottom: 8}}></div>
      <div className="skeleton-content" style={{width: '100%', height: 48, background: '#f3f3f3', marginBottom: 8}}></div>
      <div className="skeleton-footer" style={{width: '40%', height: 16, background: '#e0e0e0'}}></div>
    </div>
  );
}