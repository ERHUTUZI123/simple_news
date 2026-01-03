// import React, { useEffect, useState } from "react";
// import { fetchTodayNews } from "../services/api";
// import NewsCard from "../components/NewsCard";

// export default function NewsList() {
//   const [news, setNews] = useState([]);

//   useEffect(() => {
//     fetchTodayNews().then(data => {
//       // Frontend initially has no voteCount, set all to 0 here, NewsCard will automatically fetch later
//       setNews(data);
//     });
//   }, []);

//   // Sort by voteCount descending (NewsCard will automatically update voteCount, sorting will take effect after initial render)
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