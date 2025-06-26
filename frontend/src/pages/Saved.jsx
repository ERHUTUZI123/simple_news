import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// 格式化相对时间
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

// Export bookmarks as Markdown format
function exportToMarkdown(savedArticles) {
  let content = "# My Saved Articles\n\n";
  content += `Total: ${savedArticles.length} articles\n\n`;
  
  savedArticles.forEach((article, index) => {
    content += `## ${index + 1}. ${article.title}\n\n`;
    content += `**Source**: ${article.source}\n\n`;
    content += `**Time**: ${formatRelativeTime(article.date)}\n\n`;
    content += `**Original**: [${article.link}](${article.link})\n\n`;
    if (article.summary) {
      content += `**Summary**: ${article.summary}\n\n`;
    }
    content += "---\n\n";
  });
  
  return content;
}

// Export bookmarks as TXT format
function exportToTxt(savedArticles) {
  let content = "My Saved Articles\n\n";
  content += `Total: ${savedArticles.length} articles\n\n`;
  
  savedArticles.forEach((article, index) => {
    content += `${index + 1}. ${article.title}\n`;
    content += `Source: ${article.source}\n`;
    content += `Time: ${formatRelativeTime(article.date)}\n`;
    content += `Original: ${article.link}\n`;
    if (article.summary) {
      content += `Summary: ${article.summary}\n`;
    }
    content += "\n";
  });
  
  return content;
}

// Download file
function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function Saved() {
  const [savedArticles, setSavedArticles] = useState([]);
  const [removedArticle, setRemovedArticle] = useState(null);
  const [showUndo, setShowUndo] = useState(false);
  const navigate = useNavigate();

  // Load bookmarked articles
  useEffect(() => {
    const saved = localStorage.getItem('savedArticles') || '[]';
    setSavedArticles(JSON.parse(saved));
  }, []);

  // Save bookmarks to localStorage
  const saveToStorage = (articles) => {
    localStorage.setItem('savedArticles', JSON.stringify(articles));
    setSavedArticles(articles);
  };

  // Remove bookmark
  const removeFromSaved = (articleToRemove) => {
    const updatedArticles = savedArticles.filter(article => article.title !== articleToRemove.title);
    saveToStorage(updatedArticles);
    setRemovedArticle(articleToRemove);
    setShowUndo(true);
    
    // Auto-hide undo button after 5 seconds
    setTimeout(() => {
      setShowUndo(false);
      setRemovedArticle(null);
    }, 5000);
  };

  // Undo remove
  const undoRemove = () => {
    if (removedArticle) {
      const updatedArticles = [...savedArticles, removedArticle];
      saveToStorage(updatedArticles);
      setRemovedArticle(null);
      setShowUndo(false);
    }
  };

  // Export bookmarks
  const exportSaved = (format = 'md') => {
    if (savedArticles.length === 0) {
      alert('No articles to export');
      return;
    }

    const timestamp = new Date().toISOString().split('T')[0];
    if (format === 'md') {
      const content = exportToMarkdown(savedArticles);
      downloadFile(content, `saved-articles-${timestamp}.md`, 'text/markdown');
    } else {
      const content = exportToTxt(savedArticles);
      downloadFile(content, `saved-articles-${timestamp}.txt`, 'text/plain');
    }
  };

  // 跳转到文章详情页
  const goToArticle = (title) => {
    const slug = encodeURIComponent(title);
    navigate(`/article/${slug}`);
  };

  return (
    <div className="news-container">
      {/* Page title */}
      <div style={{
        textAlign: "center",
        marginBottom: "2rem",
      }}>
        <h1 style={{
          fontSize: "2rem",
          marginBottom: "1rem",
          color: "var(--text-color)",
          fontFamily: "var(--font-mono)",
          fontWeight: "700",
        }}>
          # My Saved Articles
        </h1>
        <p style={{
          color: "var(--secondary-color)",
          fontSize: "1rem",
          fontFamily: "var(--font-mono)",
        }}>
          Total: {savedArticles.length} articles
        </p>
      </div>

      {/* Export buttons */}
      {savedArticles.length > 0 && (
        <div style={{
          display: "flex",
          gap: "1rem",
          justifyContent: "center",
          marginBottom: "2rem",
          flexWrap: "wrap",
        }}>
          <button
            onClick={() => exportSaved('md')}
            style={{
              background: "var(--show-summary-bg)",
              border: "1px solid var(--border-color)",
              color: "var(--show-summary-text)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.9rem",
              cursor: "pointer",
              padding: "0.75rem 1.5rem",
              borderRadius: "0.25rem",
              transition: "all 0.2s ease",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
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
            📂 Export All (.md)
          </button>
          
          <button
            onClick={() => exportSaved('txt')}
            style={{
              background: "var(--show-summary-bg)",
              border: "1px solid var(--border-color)",
              color: "var(--show-summary-text)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.9rem",
              cursor: "pointer",
              padding: "0.75rem 1.5rem",
              borderRadius: "0.25rem",
              transition: "all 0.2s ease",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = "var(--button-hover-bg)";
              e.target.style.color = "var(--button-hover-text)";
              e.target.style.borderColor = "var(--button-hover-border)";
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = "var(--show-summary-bg)";
              e.target.style.color = "var(--show-summary-text)";
              e.target.style.borderColor = "var(--border-color)";
            }}
          >
            📄 Export as TXT
          </button>
        </div>
      )}

      {/* Bookmark list */}
      {savedArticles.length === 0 ? (
        <div style={{
          textAlign: "center",
          padding: "3rem 1rem",
          color: "var(--secondary-color)",
        }}>
          <div style={{
            fontSize: "3rem",
            marginBottom: "1rem",
          }}>
            📚
          </div>
          <p style={{
            fontSize: "1.1rem",
            fontFamily: "var(--font-mono)",
            marginBottom: "0.5rem",
          }}>
            No saved articles yet
          </p>
          <p style={{
            fontSize: "0.9rem",
            fontFamily: "var(--font-mono)",
          }}>
            Click ⭐ Save on any article to add it here
          </p>
        </div>
      ) : (
        <div>
          {savedArticles.map((article, index) => (
            <div
              key={`${article.title}-${index}`}
              className="news-card"
              style={{
                animation: "fadeIn 0.4s ease-in-out",
                animationDelay: `${index * 0.1}s`,
              }}
            >
              {/* Source and time */}
              <div className="meta">
                <span style={{ color: "var(--highlight-color)" }}>✅</span> {article.source} 
                <span style={{ margin: "0 0.5rem" }}>🕒</span> {formatRelativeTime(article.date)}
              </div>

              {/* Title */}
              <h3 className="title">
                <a href={article.link} target="_blank" rel="noopener noreferrer">
                  # {article.title}
                </a>
              </h3>

              {/* AI Summary */}
              {article.summary && (
                <div className="expanded-summary">
                  <p style={{
                    margin: "0.5rem 0",
                    lineHeight: "1.6",
                    color: "var(--text-color)",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.9rem",
                  }}>
                    - {article.summary}
                  </p>
                </div>
              )}

              {/* Action buttons */}
              <div className="actions">
                <button
                  onClick={() => goToArticle(article.title)}
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
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.5rem",
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
                  href={article.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{
                    color: "var(--view-original-text)",
                    textDecoration: "none",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.9rem",
                    padding: "0.5rem 1rem",
                    border: "1px solid var(--view-original-border)",
                    borderRadius: "0.25rem",
                    transition: "all 0.2s ease",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    backgroundColor: "transparent",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = "var(--button-hover-bg)";
                    e.target.style.color = "var(--button-hover-text)";
                    e.target.style.borderColor = "var(--button-hover-border)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = "transparent";
                    e.target.style.color = "var(--view-original-text)";
                    e.target.style.borderColor = "var(--view-original-border)";
                  }}
                >
                  🔗 View Original
                </a>

                <button
                  onClick={() => removeFromSaved(article)}
                  style={{
                    background: "none",
                    border: "1px solid var(--border-color)",
                    color: "var(--text-color)",
                    fontFamily: "var(--font-mono)",
                    fontSize: "0.9rem",
                    cursor: "pointer",
                    padding: "0.5rem 1rem",
                    borderRadius: "0.25rem",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = "var(--trash-hover-bg)";
                    e.target.style.color = "var(--trash-hover-text)";
                    e.target.style.borderColor = "var(--trash-hover-border)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = "transparent";
                    e.target.style.color = "var(--text-color)";
                    e.target.style.borderColor = "var(--border-color)";
                  }}
                >
                  🗑️ Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Toast 通知 */}
      {showUndo && (
        <div style={{
          position: "fixed",
          bottom: "2rem",
          left: "50%",
          transform: "translateX(-50%)",
          background: "var(--bg-color)",
          color: "var(--text-color)",
          border: "1px solid var(--border-color)",
          borderRadius: "0.5rem",
          padding: "1rem 1.5rem",
          fontFamily: "var(--font-mono)",
          fontSize: "0.9rem",
          zIndex: 1000,
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
        }}>
          <span>Removed from saved</span>
          <button
            onClick={undoRemove}
            style={{
              background: "var(--show-summary-bg)",
              border: "1px solid var(--border-color)",
              color: "var(--show-summary-text)",
              fontFamily: "var(--font-mono)",
              fontSize: "0.8rem",
              cursor: "pointer",
              padding: "0.25rem 0.5rem",
              borderRadius: "0.25rem",
              transition: "all 0.2s ease",
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
            Undo
          </button>
        </div>
      )}
    </div>
  );
} 