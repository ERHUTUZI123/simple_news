// import React, { useEffect, useState } from "react";
// import { fetchTodayNews } from "../services/api";
// import NewsCard from "../components/NewsCard";

// export default function NewsList() {
//   const [news, setNews] = useState([]);

//   useEffect(() => {
//     fetchTodayNews().then(data => {
//       // 前端初始没有 voteCount，这里先全部设为 0，后续 NewsCard 会自动拉取
//       setNews(data);
//     });
//   }, []);

//   // 按 voteCount 降序排序（NewsCard 会自动更新 voteCount，排序会在初次渲染后生效）
//   const sortedNews = [...news].sort(
//     (a, b) => (b.voteCount ?? 0) - (a.voteCount ?? 0)
//   );

//   return (
//     <div>
//       {sortedNews.map(item => (
//         <NewsCard key={item.title} {...item} />
//       ))}
//     </div>
//   );
// }