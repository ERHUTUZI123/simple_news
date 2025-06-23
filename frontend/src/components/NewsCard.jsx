import React, { useState, useEffect } from "react";
import {
  fetchSummary,
  fetchScore,
  voteNews,
  downvoteNews,
  fetchVote
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

const BAR_LENGTH = 20;

export default function NewsCard({ title, link, date, source, content }) {
  const [expanded, setExpanded] = useState(false);
  const [tldr, setTldr] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isHeadline, setIsHeadline] = useState(false);
  const [isTrash, setIsTrash] = useState(false);
  const [voteCount, setVoteCount] = useState(null);
  const [aiScore, setAiScore] = useState(null);

  // 初始：加载投票数
  useEffect(() => {
    let mounted = true;
    fetchVote(title)
      .then(count => mounted && setVoteCount(count))
      .catch(() => mounted && setVoteCount(null));
    return () => { mounted = false; };
  }, [title]);

  // 初始：加载 AI 打分
  useEffect(() => {
    let mounted = true;
    fetchScore(content)
      .then(score => mounted && setAiScore(score))
      .catch(() => mounted && setAiScore(null));
    return () => { mounted = false; };
  }, [content]);

  // 进度条
  useEffect(() => {
    let timer;
    if (loading) {
      setProgress(0);
      timer = setInterval(() => {
        setProgress(p => Math.min(p + Math.floor(Math.random() * 10) + 1, 98));
      }, 100);
    }
    return () => clearInterval(timer);
  }, [loading]);

  useEffect(() => {
    if (!loading && expanded) setProgress(100);
  }, [loading, expanded]);

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
      const count = await downvoteNews(title);
      setVoteCount(count);
    } else {
      setIsHeadline(true);
      setIsTrash(false);
      const count = await voteNews(title);
      setVoteCount(count);
    }
  };

  // 垃圾或撤销
  const toggleTrash = async () => {
    if (isTrash) {
      setIsTrash(false);
      const count = await voteNews(title);
      setVoteCount(count);
    } else {
      setIsTrash(true);
      setIsHeadline(false);
      setExpanded(false);
      const count = await downvoteNews(title);
      setVoteCount(count);
    }
  };

  // 进度展示组件
  const renderBar = () => {
    const pct = Math.round(progress);
    const done = Math.round((pct / 100) * BAR_LENGTH);
    const todo = BAR_LENGTH - done;
    return (
      <div className="progress-bar">
        {["#".repeat(done), "-".repeat(todo)]} {pct}%
      </div>
    );
  };

  return (
    <div className={`news-card${isHeadline ? " headline" : ""}${isTrash ? " trash" : ""}`}>
      {/* 标题与链接 */}
      <a href={link} target="_blank" rel="noopener noreferrer" className="title">
        {title}
        {isHeadline && <span className="badge">HEADLINE</span>}
      </a>
      {/* 来源和相对时间 */}
      <div className="meta">
        {source} · {formatRelativeTime(date)}
      </div>
      {/* AI 评分 */}
      {aiScore !== null && (
        <div className="ai-score">[{aiScore}]</div>
      )}
      {/* 加载进度 */}
      {expanded && loading && renderBar()}
      {/* 摘要区域 */}
      <div className={`summary-container${expanded && !loading ? " expanded" : ""}`}>
        {expanded && !loading && <p className="expanded-summary">{tldr}</p>}
      </div>
      {/* 操作按钮 */}
      <div className="actions" style={{ justifyContent: isTrash ? "flex-start" : "space-between" }}>
        {!isTrash && (
          <>
            <button className="action-button" onClick={handleTldr}>
              {expanded ? "Hide TLDR" : "Show TLDR"}
            </button>
            <button className="action-button action-headline" onClick={toggleHeadline}>
              {isHeadline ? "Undo Headline" : "👍 Headline"}
            </button>
          </>
        )}
        {!isHeadline && (
          <button className="action-button action-trash" onClick={toggleTrash}>
            {isTrash ? "Undo Trash" : "💩 Trash"}
          </button>
        )}
      </div>
    </div>
  );
}