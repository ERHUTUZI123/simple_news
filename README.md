OneMinNews – AI-Powered News Aggregator with LLM-Based AI Agent

Overview
--------
OneMinNews is a scalable news aggregation application designed to automatically digest, summarize,
and prioritize large volumes of news content. At its core is an **AI AGENT** powered by a fine-tuned
large language model that ingests up to ~30,000 news articles per day, generates concise summaries,
and assigns importance scores to support rapid understanding and downstream decision-making.

The system combines modern web technologies with a distributed LLM training and inference pipeline,
delivering both a clean user-facing reading experience and a robust backend suitable for research
and analytics workflows.

AI Agent Architecture
---------------------
The **AI AGENT** is built around a 7B-parameter instruction-tuned language model adapted using
parameter-efficient fine-tuning (PEFT) on ~24K programmatically generated article–summary pairs.

Key characteristics:
- Distributed training and inference using PyTorch and DeepSpeed
- HuggingFace Transformers for model integration and deployment
- Efficient batching and caching to support high-throughput, low-latency inference
- Automated news ingestion, summarization, and importance scoring
- Structured outputs designed for dashboards, analytics, or research pipelines

The agent is exposed via a FastAPI service, enabling real-time interaction with frontend clients
and external systems.

Key Features
------------
1. AI Summary Reading Page
   - Access:
     - /article/:id – Access by article ID
     - /summary/:slug – Access by article title
   - Features:
     - **AI AGENT**-generated summaries with detailed / brief toggle
     - Importance-aware summarization for rapid prioritization
     - Original article link, bookmarking, and sharing
     - Local caching to reduce latency and repeated inference calls
   - Design:
     - Minimalist black-and-white theme focused on reading
     - Monospace font for clarity and consistency
     - Responsive layout with subtle micro-animations

2. Bookmarks Page
   - Access: /saved
   - Features:
     - View, manage, and remove saved articles
     - Real-time synchronization of bookmark state across pages
     - Export bookmarks as Markdown (.md) or plain text (.txt)
     - Undo removal with Toast-based feedback
   - User Experience:
     - Smooth card animations and mobile-friendly design
     - Empty state guidance for new users

3. Quick Actions
   - Bookmark articles from homepage cards or summary pages
   - One-click access to **AI AGENT** summaries or original sources
   - Export curated reading lists with summaries and metadata

Technical Stack
---------------
Frontend
- Framework: React 18 + React Router
- Styling: CSS variables, responsive design
- State & Storage: localStorage for bookmarks and summary caching

Backend & AI Agent
- API Framework: FastAPI
- Language: Python
- Database Layer: SQLAlchemy
- LLM Stack:
  - PyTorch for model training and inference
  - DeepSpeed for distributed, memory-efficient execution
  - HuggingFace Transformers for model loading and integration
  - OpenAI API (optional / fallback) for summary generation
- Functionality:
  - Automated news scraping and ingestion
  - High-throughput summarization and rating
  - REST APIs:
    - GET /news/article?title={title}
    - GET /news/article/{id}

Data Management
---------------
- Local caching of **AI AGENT** summaries to minimize repeated inference
- High-throughput batching for streaming news data
- Real-time synchronization of bookmark state across views
- Export support in Markdown and TXT formats

Getting Started
---------------
Run Locally:

Backend
cd backend
python main.py

Frontend
cd frontend
npm run dev

Access
- Frontend: http://localhost:5175
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

Notes
-----
- Requires OpenAI API key configuration (if enabled)
- Initial summary generation requires network access
- Cached summaries remain available for offline reading
- Bookmark data is stored locally in the browser

<<<<<<< HEAD
1. **API Dependencies**: Need to configure OpenAI API key
2. **Network Requests**: First summary generation requires network connection
3. **Caching Mechanism**: Summary results will be cached in browser local storage
4. **Error Handling**: Mock data will be displayed when API fails
5. **Data Persistence**: Bookmark data is saved in browser localStorage

### Future Improvements


---

## Scalable News Summarization & Rating AI Agent (Backend)

This project features a scalable news summarization and rating AI agent designed to automatically digest and prioritize high volumes of news content. The system leverages a 7B-parameter instruction-tuned language model (LLM) using parameter-efficient fine-tuning on ~24K article–summary pairs, and is built for distributed training and inference with PyTorch and DeepSpeed. It ingests ~30,000 articles per day, summarizes them, and produces an importance score for downstream decision-making or research dashboards.

### Backend Tech Stack
- **Python** (core language)
- **FastAPI** (real-time API)
- **PyTorch** (deep learning framework)
- **DeepSpeed** (distributed training/inference)
- **HuggingFace Transformers** (LLM integration)
- **Efficient batching & caching** (for low-latency, high-throughput inference)
- **Structured outputs** (for downstream integration)

### Key Features
- Distributed, scalable summarization and scoring pipeline
- Real-time API endpoints for summarization and importance scoring
- Efficient batching and caching to handle streaming data
- Model integration via HuggingFace and DeepSpeed

### Example API Usage

**Summarize a single article:**
```
POST /summarize
{
	"article": "<news article text>"
}
```
Response:
```
{
	"summary": "...",
	"score": 0.87
}
```

**Batch summarization:**
```
POST /batch_summarize
{
	"articles": ["article1 text", "article2 text", ...]
}
```
Response:
```
{
	"summaries": ["...", "..."],
	"scores": [0.87, 0.65]
}
```

### Running the API

1. Install dependencies:
	 ```
	 pip install -r backend/requirements.txt
	 ```
2. Start the FastAPI server:
	 ```
	 uvicorn backend.app.api:app --reload
	 ```

### Model & Inference
- Model is loaded via HuggingFace Transformers and optionally accelerated with DeepSpeed for distributed inference.
- Summarization and scoring are batched and cached for efficiency.

---
=======
Future Improvements
-------------------
- Additional summary and reasoning formats
- Cloud-based user and bookmark synchronization
- Reading history and behavioral analytics
- Bookmark classification, search, and filtering
- Offline-first reading mode
- Extended AI AGENT reasoning and RAG-based retrieval
>>>>>>> edf1ad577c9dd272a837f5be3188b081bb2e90d2
