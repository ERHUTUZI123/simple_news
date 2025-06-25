import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// 格式化相对时间
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

// 导出收藏为Markdown格式
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

// 导出收藏为TXT格式
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

// 下载文件
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
  const navigate = useNavigate();
  const [savedArticles, setSavedArticles] = useState([]);
  const [removedArticles, setRemovedArticles] = useState([]);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [lastRemovedArticle, setLastRemovedArticle] = useState(null);

  // 加载收藏的文章
  useEffect(() => {
    const saved = localStorage.getItem('savedArticles');
    if (saved) {
      setSavedArticles(JSON.parse(saved));
    }
  }, []);

  // 保存收藏到localStorage
  const saveToStorage = (articles) => {
    localStorage.setItem('savedArticles', JSON.stringify(articles));
  };

  // 移除收藏
  const removeFromSaved = (articleToRemove) => {
    const updatedArticles = savedArticles.filter(article => 
      article.title !== articleToRemove.title
    );
    setSavedArticles(updatedArticles);
    setRemovedArticles([...removedArticles, articleToRemove]);
    setLastRemovedArticle(articleToRemove);
    saveToStorage(updatedArticles);
    
    // 显示Toast
    setToastMessage("Removed from saved");
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // 撤销移除
  const undoRemove = () => {
    if (lastRemovedArticle) {
      const updatedArticles = [...savedArticles, lastRemovedArticle];
      setSavedArticles(updatedArticles);
      setRemovedArticles(removedArticles.filter(article => 
        article.title !== lastRemovedArticle.title
      ));
      setLastRemovedArticle(null);
      saveToStorage(updatedArticles);
      
      setToastMessage("Undo successful");
      setShowToast(true);
      setTimeout(() => setShowToast(false), 2000);
    }
  };

  // 导出收藏
  const exportSaved = (format = 'md') => {
    if (savedArticles.length === 0) {
      setToastMessage("No saved articles to export");
      setShowToast(true);
      setTimeout(() => setShowToast(false), 2000);
      return;
    }

    const timestamp = new Date().toISOString().split('T')[0];
    let content, filename, type;

    if (format === 'md') {
      content = exportToMarkdown(savedArticles);
      filename = `saved-articles-${timestamp}.md`;
      type = 'text/markdown';
    } else {
      content = exportToTxt(savedArticles);
      filename = `saved-articles-${timestamp}.txt`;
      type = 'text/plain';
    }

    downloadFile(content, filename, type);
    
    setToastMessage(`Exported ${savedArticles.length} articles`);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2000);
  };

  // 跳转到文章详情页
  const goToArticle = (title) => {
    const slug = encodeURIComponent(title);
    navigate(`/article/${slug}`);
  };

  return (
    <div className="news-container">
      {/* 页面标题 */}
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

      {/* 导出按钮 */}
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
              background: "var(--highlight-color)",
              border: "none",
              color: "var(--bg-color)",
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
            }}
            onMouseLeave={(e) => {
              e.target.style.opacity = "1";
            }}
          >
            📂 Export All (.md)
          </button>
          
          <button
            onClick={() => exportSaved('txt')}
            style={{
              background: "none",
              border: "1px solid var(--border-color)",
              color: "var(--text-color)",
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
              e.target.style.backgroundColor = "var(--text-color)";
              e.target.style.color = "var(--bg-color)";
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = "transparent";
              e.target.style.color = "var(--text-color)";
            }}
          >
            📄 Export as TXT
          </button>
        </div>
      )}

      {/* 收藏列表 */}
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
              {/* 来源和时间 */}
              <div className="meta">
                <span style={{ color: "var(--highlight-color)" }}>✅</span> {article.source} 
                <span style={{ margin: "0 0.5rem" }}>🕒</span> {formatRelativeTime(article.date)}
              </div>

              {/* 标题 */}
              <h3 className="title">
                <a href={article.link} target="_blank" rel="noopener noreferrer">
                  # {article.title}
                </a>
              </h3>

              {/* AI 摘要 */}
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

              {/* 操作按钮 */}
              <div className="actions">
                <button
                  onClick={() => goToArticle(article.title)}
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
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.5rem",
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
                  href={article.link} 
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
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.5rem",
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
                  🔗 View Original
                </a>

                <button
                  onClick={() => removeFromSaved(article)}
                  style={{
                    background: "none",
                    border: "1px solid var(--trash-color)",
                    color: "var(--trash-color)",
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
                    e.target.style.backgroundColor = "var(--trash-color)";
                    e.target.style.color = "var(--bg-color)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = "transparent";
                    e.target.style.color = "var(--trash-color)";
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
      {showToast && (
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
          <span>{toastMessage}</span>
          {lastRemovedArticle && (
            <button
              onClick={undoRemove}
              style={{
                background: "var(--highlight-color)",
                border: "none",
                color: "var(--bg-color)",
                fontFamily: "var(--font-mono)",
                fontSize: "0.8rem",
                cursor: "pointer",
                padding: "0.25rem 0.5rem",
                borderRadius: "0.25rem",
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.target.style.opacity = "0.8";
              }}
              onMouseLeave={(e) => {
                e.target.style.opacity = "1";
              }}
            >
              Undo
            </button>
          )}
        </div>
      )}
    </div>
  );
} 