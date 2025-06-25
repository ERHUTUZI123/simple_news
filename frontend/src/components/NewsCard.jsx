import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  fetchSummary,
  voteNews,
  downvoteNews,
} from "../services/api";

// 简单去除 HTML 标签
function stripHtml(html) {
  const tmp = document.createElement("div");
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || "";
}

// 格式化相对时间（展示分钟 m、小时 h、天 d）
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

export default function NewsCard({ title, link, date, source, content, ai_score, comprehensive_score, vote_count }) {
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState(false);
  const [tldr, setTldr] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isHeadline, setIsHeadline] = useState(false);
  const [isTrash, setIsTrash] = useState(false);

  // 检查文章是否已收藏
  useEffect(() => {
    const saved = localStorage.getItem('savedArticles');
    if (saved) {
      const savedArticles = JSON.parse(saved);
      const isArticleSaved = savedArticles.some(article => article.title === title);
      setIsSaved(isArticleSaved);
    }
  }, [title]);

  // 点击生成或隐藏摘要
  const handleTldr = async () => {
    if (tldr) {
      setExpanded(!expanded);
      return;
    }
    setLoading(true);
    setExpanded(true);

    const key = `tldr-${title}`;
    const cached = localStorage.getItem(key);
    if (cached) {
      setTldr(stripHtml(cached));
      setLoading(false);
      return;
    }

    try {
      const s = await fetchSummary(content);
      localStorage.setItem(key, s);
      setTldr(stripHtml(s));
    } catch {
      setTldr("Generation failed, try again later.");
    } finally {
      setLoading(false);
    }
  };

  // 点赞或撤销
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

  // 垃圾或撤销
  const toggleTrash = async () => {
    if (isTrash) {
      setIsTrash(false);
      await voteNews(title);
    } else {
      setIsTrash(true);
      setIsHeadline(false);
      setExpanded(false);
      await downvoteNews(title);
    }
  };

  // 收藏功能
  const toggleSaved = () => {
    const saved = localStorage.getItem('savedArticles') || '[]';
    const savedArticles = JSON.parse(saved);
    
    if (isSaved) {
      // 移除收藏
      const updatedArticles = savedArticles.filter(article => article.title !== title);
      localStorage.setItem('savedArticles', JSON.stringify(updatedArticles));
      setIsSaved(false);
    } else {
      // 添加收藏
      const articleToSave = {
        title,
        link,
        date,
        source,
        content,
        summary: tldr || ""
      };
      const updatedArticles = [...savedArticles, articleToSave];
      localStorage.setItem('savedArticles', JSON.stringify(updatedArticles));
      setIsSaved(true);
    }
  };

  // 跳转到Article页面
  const goToArticle = () => {
    // 使用title作为slug，实际项目中应该使用唯一的ID
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
        {ai_score && (
          <span style={{ margin: "0 0.5rem", color: "var(--secondary-color)" }}>
            🤖 AI: {ai_score}/10
          </span>
        )}
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

      {/* AI 摘要 */}
      <div className="summary-section">
        {!expanded && !loading && (
          <button 
            className="tldr-button" 
            onClick={handleTldr}
            style={{
              background: "none",
              border: "none",
              color: "var(--text-color)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.9rem",
              cursor: "pointer",
              padding: "0.5rem 0",
              textDecoration: "none",
            }}
          >
            - Show AI Summary
          </button>
        )}
        
        {loading && (
          <div style={{ 
            color: "var(--secondary-color)", 
            fontFamily: "var(--font-mono)",
            fontSize: "0.9rem",
            padding: "0.5rem 0"
          }}>
            Generating AI summary...
          </div>
        )}
        
        {expanded && !loading && tldr && (
          <div className="expanded-summary">
            <p style={{
              margin: "0.5rem 0",
              lineHeight: "1.6",
              color: "var(--text-color)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.9rem",
              maxHeight: "6rem",
              overflow: "hidden",
              textOverflow: "ellipsis",
              display: "-webkit-box",
              WebkitLineClamp: 4,
              WebkitBoxOrient: "vertical",
            }}>
              - {tldr}
            </p>
            <button 
              className="tldr-button" 
              onClick={() => setExpanded(false)}
              style={{
                background: "none",
                border: "none",
                color: "var(--secondary-color)",
                fontFamily: "var(--font-mono)",
                fontSize: "0.8rem",
                cursor: "pointer",
                padding: "0.25rem 0",
                textDecoration: "none",
              }}
            >
              Hide Summary
            </button>
          </div>
        )}
      </div>

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
          {isHeadline ? "Undo Headline" : "👍 Headline"}
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
          {isTrash ? "Undo Trash" : "💩 Trash"}
        </button>
      </div>
    </div>
  );
}