const API_BASE = import.meta.env.VITE_API_BASE;

export function fetchTodayNews(offset = 0, limit = 10) {
  return fetch(`${API_BASE}/news/today?offset=${offset}&limit=${limit}`)
    .then(res => {
      if (!res.ok) throw new Error("API error");
      return res.json();
    });
}

// export function fetchSummary(content) {
//   return axios
//     .post("/news/summary", { content })
//     .then(res => res.data.summary);
// }

// export function fetchScore(content) {
//   return axios
//     .get("/news/score", { params: { text: content } })
//     .then(res => res.data.ai_score);
// }

export function voteNews(title, delta = 1) {
  return axios
    .post("/news/vote", null, { params: { title, delta } })
    .then(res => res.data.count);
}

export function downvoteNews(title) {
  return voteNews(title, -1);
}

export function fetchVote(title) {
  return axios
    .get("/news/vote", { params: { title } })
    .then(res => res.data.count);
}

export function createCheckoutSession() {
  return fetch("/create-checkout-session", {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  })
    .then(res => res.json())
    .then(data => data.url);
}