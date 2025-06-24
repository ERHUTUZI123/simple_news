import { useState, useEffect, useRef } from "react";
import { fetchTodayNews, fetchVote, fetchScore, createCheckoutSession } from "../services/api";
import NewsCard from "../components/NewsCard";
import { motion, AnimatePresence } from "framer-motion";

const equivalents = [
  "1/8 ice cream 🍦",
  "1/3 coffee ☕️",
  "1/10 movie ticket 🎬",
  "1/5 subway ride 🚇",
  "1/20 burger 🍔",
  "1/4 croissant 🥐",
  "1/6 bubble tea 🧋",
  "1/15 museum ticket 🖼️",
  "1/12 donut 🍩",
];

export default function Home() {
  const [newsList, setNewsList] = useState([]);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showSubscribe, setShowSubscribe] = useState(false);
  const [equivIdx, setEquivIdx] = useState(0);
  const [sortType, setSortType] = useState("time"); // 新增排序类型
  const observerRef = useRef(null);
  const LIMIT = 10;

  const loadMoreNews = async () => {
    if (loading || showSubscribe) return;
    setLoading(true);
    try {
      const data = await fetchTodayNews(offset, LIMIT);
      const enriched = await Promise.all(
        data.map(async (item) => {
          const count = await fetchVote(item.title).catch(() => 0);
          // 新增：获取AI分数
          const aiScore = await fetchScore(item.content).catch(() => null);
          return { ...item, voteCount: count, aiScore };
        })
      );
      setNewsList(prevList => {
        const updatedList = [...prevList, ...enriched];
        if (updatedList.length >= 20) setShowSubscribe(true);
        return updatedList;
      });
      setOffset(prev => prev + LIMIT);
    } catch (e) {
      console.error("❌ Failed to load news:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!showSubscribe) return;
    const timer = setInterval(() => {
      setEquivIdx((prev) => (prev + 1) % equivalents.length);
    }, 2000);
    return () => clearInterval(timer);
  }, [showSubscribe]);

  useEffect(() => {
    loadMoreNews();
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) loadMoreNews();
      },
      { threshold: 1 }
    );
    if (observerRef.current) observer.observe(observerRef.current);
    return () => observer.disconnect();
  }, [newsList]);

  // 排序逻辑
  let sortedNews = [...newsList];
  if (sortType === "time") {
    sortedNews.sort((a, b) => new Date(b.date) - new Date(a.date));
  } else if (sortType === "score") {
    sortedNews.sort((a, b) => (b.aiScore ?? 0) - (a.aiScore ?? 0)); // ✅ 注意这里是 aiScore
  }


  return (
    <div className="news-container">
      {/* 排序按钮 */}
      <div style={{ display: "flex", justifyContent: "center", gap: "1rem", marginBottom: "1.5rem" }}>
        {[
          { label: "Sort by Time", value: "time" },
          { label: "Sort by AI Score", value: "score" },
        ].map(({ label, value }) => (
          <button
            key={value}
            onClick={() => setSortType(value)}
            style={{
              backgroundColor: sortType === value ? "#fff" : "transparent",
              color: sortType === value ? "#000" : "#fff",
              border: "1px solid #fff",
              borderRadius: "999px",
              padding: "0.5rem 1.2rem",
              fontFamily: "monospace",
              fontSize: "0.95rem",
              cursor: "pointer",
              transition: "all 0.3s ease",
            }}
          >
            {label}
          </button>
        ))}
      </div>


      {/* 新闻列表 */}
      {sortedNews.map((n) => (
        <NewsCard key={n.title} {...n} />
      ))}

      {/* 订阅弹窗或加载更多 */}
      {showSubscribe ? (
        <div className="subscribe-popup">
          <h3 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>
            Only $0.3/day =
            <AnimatePresence mode="wait">
              <motion.span
                key={equivIdx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.4 }}
                style={{ marginLeft: "0.5rem", color: "#fffff" }}
              >
                {equivalents[equivIdx]}
              </motion.span>
            </AnimatePresence>
          </h3>
          <p style={{ fontSize: "1rem", marginBottom: "1rem" }}>
            Subscribe for more curated daily insights.
          </p>
          <button
            onClick={async () => {
              const url = await createCheckoutSession();
              window.location.href = url;
            }}
            className="subscribe-popup"
          >
            Subscribe
          </button>
        </div>
      ) : (
        <div ref={observerRef} style={{ height: 40 }} />
      )}

      {loading && <p style={{ textAlign: "center", marginTop: "1rem" }}>Loading...</p>}
    </div>
  );
}
