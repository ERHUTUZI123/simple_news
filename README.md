# OneMinNews - Tech News Aggregator

## Overview

OneMinNews is a news aggregation application that provides AI-powered summaries and bookmark management, allowing users to quickly understand news highlights and manage their personal collections.

## New Features: AI Summary Reading Page

### Page Paths
- `/article/:id` - Access by article ID
- `/summary/:slug` - Access by article title

### Features

#### 1. Page Structure
- **Top Navigation**: Logo + Back to Home button
- **Article Information**: Source, publish time, title
- **AI Summary**: Support for detailed/brief version toggle
- **Auxiliary Functions**: Original link, bookmark, share

#### 2. Core Features
- **AI Summary Generation**: Click button to generate AI summary
- **Summary Type Toggle**: Switch between detailed and brief versions
- **Local Caching**: Summary results cached in localStorage
- **Bookmark Function**: Save interesting articles
- **Share Function**: Support native sharing or copy link

#### 3. Visual Design
- **Minimalist Style**: Black and white color scheme, focused on reading experience
- **Code Font**: Use monospace font to improve readability
- **Responsive Design**: Adapt to various screen sizes
- **Micro-animations**: fadeIn animation enhances user experience

## New Features: Bookmarks Page

### Page Path
- `/saved` - Bookmarks page

### Features

#### 1. Page Structure
- **Page Title**: # My Saved Articles
- **Bookmark Count**: Display current bookmark count
- **Export Function**: Support Markdown and TXT format export
- **Bookmark List**: Consistent structure with homepage news cards

#### 2. Core Features
- **Bookmark Management**: View, remove bookmarked articles
- **State Synchronization**: Real-time synchronization of bookmark status across all pages
- **Export Function**: Support .md and .txt format export
- **Undo Function**: Support undo operation after removing bookmarks
- **Quick Access**: One-click jump to article summary page

#### 3. Interactive Experience
- **Toast Notifications**: Operation feedback and undo prompts
- **Animation Effects**: Card fade-in animation
- **Responsive Design**: Mobile adaptation
- **Empty State Prompt**: Guide users to bookmark articles

### Usage

#### Bookmark Articles
1. Click the **"⭐ Save"** button on any news card on the homepage
2. Click the **"⭐ Save"** button on the AI summary reading page
3. Bookmark status will automatically sync across all pages

#### Manage Bookmarks
1. Click **"Saved"** in the navigation bar to enter the bookmarks page
2. View all bookmarked articles
3. Click **"🗑️ Remove"** to delete unwanted articles
4. After removal, you can restore via the **"Undo"** button in the Toast

#### Export Bookmarks
1. Click **"📂 Export All (.md)"** or **"📄 Export as TXT"** on the bookmarks page
2. Files will be automatically downloaded to local
3. Contains article title, source, time, link and summary information

#### Quick Access
- Click **"📖 Read Summary"** to jump to the AI summary reading page
- Click **"🔗 View Original"** to open the original article in a new tab

### Technical Implementation

#### Frontend Tech Stack
- React 18 + React Router
- CSS variables for theme switching
- localStorage for local storage
- Responsive design

#### Backend API
- FastAPI + SQLAlchemy
- OpenAI GPT-4 for summary generation
- News data scraping and storage

#### New API Endpoints
- `GET /news/article?title={title}` - Get article by title
- `GET /news/article/{id}` - Get article by ID

#### Data Storage
- **Local Storage**: Use localStorage to save bookmark data
- **Data Synchronization**: Real-time synchronization of bookmark status across all pages
- **Export Format**: Support Markdown and plain text formats

### Development

#### Start Project
```bash
# Start backend
cd backend
python main.py

# Start frontend
cd frontend
npm run dev
```

#### Access Addresses
- Frontend: http://localhost:5175
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Notes

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