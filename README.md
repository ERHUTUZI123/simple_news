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

Future Improvements
-------------------
- Additional summary and reasoning formats
- Cloud-based user and bookmark synchronization
- Reading history and behavioral analytics
- Bookmark classification, search, and filtering
- Offline-first reading mode
- Extended AI AGENT reasoning and RAG-based retrieval
