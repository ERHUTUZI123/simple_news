import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  voteNews,
  downvoteNews,
} from "../services/api";
import { toast } from "react-toastify";

// Format relative time (display minutes m, hours h, days d)
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

// Safely format keywords
function formatKeywords(keywords) {
  try {
    if (!keywords) return "";
    
    // If it's a string, try to parse as JSON
    if (typeof keywords === 'string') {
      try {
        const parsed = JSON.parse(keywords);
        if (Array.isArray(parsed)) {
          return parsed.slice(0, 3).join(", ");
        }
      } catch {
        // If parsing fails, return string directly
        return keywords;
      }
    }
    
    // If it's an array
    if (Array.isArray(keywords)) {
      return keywords.slice(0, 3).join(", ");
    }
    
    // Other cases, convert to string
    return String(keywords);
  } catch (error) {
    console.error("Error formatting keywords:", error);
    return "";
  }
}

// New: Local storage operation functions
function getSavedIds() {
  try {
    return JSON.parse(localStorage.getItem('saved_article_ids') || '[]');
  } catch {
    return [];
  }
}
function setSavedIds(ids) {
  localStorage.setItem('saved_article_ids', JSON.stringify(ids));
}

export default function NewsCard({ news, onVote }) {
  const navigate = useNavigate();
  const [isSaved, setIsSaved] = useState(() => getSavedIds().includes(news.id));
  const [isHeadline, setIsHeadline] = useState(false);
  const [isTrash, setIsTrash] = useState(false);

  // Extract data from news object
  const { id, title, link, date, source, vote_count, keywords } = news;

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

  // Save/unsave
  const onSaveClick = () => {
    let savedIds = getSavedIds();
    if (isSaved) {
      savedIds = savedIds.filter(savedId => savedId !== id);
      setSavedIds(savedIds);
      setIsSaved(false);
      toast('Article removed from saved');
    } else {
      savedIds.push(id);
      setSavedIds(savedIds);
      setIsSaved(true);
      toast('Article saved successfully!');
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
      {/* Source and time */}
      <div className="meta">
        <span style={{ color: "var(--highlight-color)" }}>✅</span> {source} 
        <span style={{ margin: "0 0.5rem" }}>🕒</span> {formatRelativeTime(date)}
        
        {/* Rating info */}
        {vote_count > 0 && (
          <span style={{ margin: "0 0.5rem", color: "var(--highlight-color)" }}>
            👍 {vote_count}
          </span>
        )}
        
        {/* Keywords display */}
        {keywords && (
          <span style={{ 
            margin: "0 0.5rem", 
            color: "var(--text-color)", 
            fontSize: "0.8rem",
            opacity: 0.7
          }}>
            🏷️ {formatKeywords(keywords)}
          </span>
        )}
      </div>

      {/* Title */}
      <h3 className="title">
        <a href={link} target="_blank" rel="noopener noreferrer">
          # {title}
        </a>
        {isHeadline && <span className="badge">HEADLINE</span>}
      </h3>

      {/* Action buttons */}
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

// Skeleton component
export function NewsCardSkeleton() {
  return (
    <div className="news-card skeleton">
      <div className="skeleton-title" style={{width: '70%', height: 24, background: '#eee', marginBottom: 8}}></div>
      <div className="skeleton-content" style={{width: '100%', height: 48, background: '#f3f3f3', marginBottom: 8}}></div>
      <div className="skeleton-footer" style={{width: '40%', height: 16, background: '#e0e0e0'}}></div>
    </div>
  );
}