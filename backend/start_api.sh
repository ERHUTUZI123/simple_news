# Run FastAPI server for news summarization and scoring

# Use this script to launch the API server with production settings

exec uvicorn backend.app.api:app --host 0.0.0.0 --port 8000 --workers 2
