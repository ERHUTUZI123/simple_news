import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  voteNews,
  downvoteNews,
} from "../services/api";

// 格式化相对时间（展示分钟 m、小时 h、天 d）
function formatRelativeTime(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMin = Math.floor(diffMs / 1000 / 60);
  
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
}

export default function NewsCard({ title, link, date, source, content, comprehensive_score, vote_count }) {
  const navigate = useNavigate();
  const [isSaved, setIsSaved] = useState(false);
  const [isHeadline, setIsHeadline] = useState(false);
  const [isTrash, setIsTrash] = useState(false);

  // Check if article is bookmarked
  useEffect(() => {
    const saved = localStorage.getItem('savedArticles');
    if (saved) {
      const savedArticles = JSON.parse(saved);
      const isArticleSaved = savedArticles.some(article => article.title === title);
      setIsSaved(isArticleSaved);
    }
  }, [title]);

  // Like or undo
  const toggleHeadline = async () => {
    if (isHeadline) {
      setIsHeadline(false);
      await downvoteNews(title);
    } else {
      setIsHeadline(true);
      setIsTrash(false);
      await voteNews(title);
    }
  };

  // Trash or undo
  const toggleTrash = async () => {
    if (isTrash) {
      setIsTrash(false);
      await voteNews(title);
    } else {
      setIsTrash(true);
      setIsHeadline(false);
      await downvoteNews(title);
    }
  };

  // Bookmark function
  const toggleSaved = () => {
    const saved = localStorage.getItem('savedArticles') || '[]';
    const savedArticles = JSON.parse(saved);
    
    if (isSaved) {
      // Remove bookmark
      const updatedArticles = savedArticles.filter(article => article.title !== title);
      localStorage.setItem('savedArticles', JSON.stringify(updatedArticles));
      setIsSaved(false);
    } else {
      // Add bookmark
      const articleToSave = {
        title,
        link,
        date,
        source,
        content,
        summary: ""  // 不再需要摘要
      };
      const updatedArticles = [...savedArticles, articleToSave];
      localStorage.setItem('savedArticles', JSON.stringify(updatedArticles));
      setIsSaved(true);
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
        {comprehensive_score && (
          <span style={{ margin: "0 0.5rem", color: "var(--text-color)", fontSize: "0.8rem" }}>
            📊 {Math.round(comprehensive_score * 100)}%
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
            background: "var(--highlight-color)",
            border: "none",
            color: "var(--bg-color)",
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
          }}
          onMouseLeave={(e) => {
            e.target.style.opacity = "1";
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
            e.target.style.backgroundColor = "var(--text-color)";
            e.target.style.color = "var(--bg-color)";
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = "transparent";
            e.target.style.color = "var(--text-color)";
          }}
        >
          View Original
        </a>

        <button
          onClick={toggleSaved}
          style={{
            background: "none",
            border: "1px solid var(--border-color)",
            color: isSaved ? "var(--highlight-color)" : "var(--text-color)",
            fontFamily: "var(--font-mono)",
            fontSize: "0.9rem",
            cursor: "pointer",
            padding: "0.5rem 1rem",
            borderRadius: "0.25rem",
            transition: "all 0.2s ease",
            marginRight: "1rem",
          }}
          onMouseEnter={(e) => {
            if (!isSaved) {
              e.target.style.backgroundColor = "var(--text-color)";
              e.target.style.color = "var(--bg-color)";
            }
          }}
          onMouseLeave={(e) => {
            if (!isSaved) {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "var(--text-color)";
            }
          }}
        >
          {isSaved ? "⭐ Saved" : "⭐ Save"}
        </button>

        <button 
          className="action-button action-headline" 
          onClick={toggleHeadline}
          style={{
            background: "none",
            border: "1px solid var(--border-color)",
            color: isHeadline ? "var(--highlight-color)" : "var(--text-color)",
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
              e.target.style.backgroundColor = "var(--text-color)";
              e.target.style.color = "var(--bg-color)";
            }
          }}
          onMouseLeave={(e) => {
            if (!isHeadline) {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "var(--text-color)";
            }
          }}
        >
          {isHeadline ? "✅ Headline" : "👍 Headline"}
        </button>

        <button 
          className="action-button action-trash" 
          onClick={toggleTrash}
          style={{
            background: "none",
            border: "1px solid var(--border-color)",
            color: isTrash ? "var(--trash-color)" : "var(--text-color)",
            fontFamily: "var(--font-mono)",
            fontSize: "0.9rem",
            cursor: "pointer",
            padding: "0.5rem 1rem",
            borderRadius: "0.25rem",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            if (!isTrash) {
              e.target.style.backgroundColor = "var(--text-color)";
              e.target.style.color = "var(--bg-color)";
            }
          }}
          onMouseLeave={(e) => {
            if (!isTrash) {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "var(--text-color)";
            }
          }}
        >
          {isTrash ? "🗑️ Trash" : "🗑️ Trash"}
        </button>
      </div>
    </div>
  );
}