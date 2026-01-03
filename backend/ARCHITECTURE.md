# System Architecture

## Overview

This document describes the architecture of the scalable news summarization and rating AI agent system, designed to process ~30,000 articles per day using a 7B-parameter instruction-tuned language model.

## System Components

### 1. Data Ingestion Layer

- **RSS Feed Parser**: Fetches articles from multiple news sources
- **Article Preprocessing**: Normalizes and validates article content
- **Storage**: PostgreSQL database for article persistence

### 2. Model Training Pipeline

```
RSS Feeds → Article Collection → Summary Generation → Training Data (~24K pairs)
                                                          ↓
                                              Fine-Tuning (PEFT/LoRA)
                                                          ↓
                                              Fine-Tuned 7B Model
```

**Key Components:**
- `generate_training_data.py`: Creates article-summary pairs
- `train_finetune.py`: Fine-tuning script with DeepSpeed ZeRO
- `ds_config.json`: DeepSpeed configuration for distributed training

### 3. Inference Engine

```
Article Input → Cache Check → Batch Processing → LLM Inference → Importance Scoring
                                      ↓
                              DeepSpeed Distributed Inference
                                      ↓
                              Structured Output
```

**Key Components:**
- `model_inference.py`: Core inference logic with batching and caching
- DeepSpeed inference for multi-GPU processing
- LRU/TTL cache for performance optimization

### 4. API Layer

- **FastAPI Application**: RESTful API endpoints
- **Structured Responses**: JSON schemas for downstream integration
- **Streaming Support**: Real-time processing endpoints
- **Health Monitoring**: System health and statistics endpoints

## Data Flow

### Training Flow

1. **Data Generation**: RSS feeds → Articles → Summaries → Training pairs
2. **Fine-Tuning**: Training pairs → LoRA fine-tuning → Fine-tuned model
3. **Model Deployment**: Fine-tuned model → Model registry → Inference service

### Inference Flow

1. **Article Ingestion**: RSS feeds → Article storage
2. **Batch Processing**: Articles → Batching → Model inference
3. **Caching**: Results cached for frequently accessed articles
4. **Output**: Structured JSON → Downstream systems

## Scalability Features

### Distributed Training
- **DeepSpeed ZeRO Stage 2**: Optimizes memory usage across GPUs
- **Model Parallelism**: Supports multi-GPU training
- **Gradient Accumulation**: Enables large effective batch sizes

### Distributed Inference
- **DeepSpeed Inference**: Multi-GPU inference with model parallelism
- **Dynamic Batching**: Optimizes throughput for varying loads
- **Smart Caching**: Reduces redundant computation

### High-Throughput Processing
- **Batch Processing**: Processes multiple articles simultaneously
- **Streaming Endpoints**: Real-time processing for continuous ingestion
- **Background Tasks**: Non-blocking operations for better responsiveness

## Performance Optimizations

1. **Caching Strategy**:
   - LRU cache for summaries (10K entries)
   - TTL cache with 24-hour expiration
   - Cache key based on article content hash

2. **Batching Strategy**:
   - Dynamic batch sizing based on load
   - Configurable batch size (default: 8)
   - Batch-aware caching

3. **Memory Optimization**:
   - FP16 precision for model weights
   - 4-bit quantization during training (QLoRA)
   - DeepSpeed ZeRO for memory efficiency

## Integration Points

### Downstream Systems
- **Research Dashboards**: Structured JSON responses
- **Decision-Making Systems**: Importance scores for prioritization
- **News Aggregation Platforms**: Summaries and metadata

### Monitoring & Observability
- Health check endpoints
- System statistics endpoints
- Cache metrics and hit rates
- Processing time tracking

## Deployment Architecture

### Development
- Single GPU inference
- Local model loading
- Basic caching

### Production
- Multi-GPU distributed inference
- Model serving with DeepSpeed
- Redis for distributed caching
- Load balancing for API endpoints

## Technology Stack

- **Deep Learning**: PyTorch, Transformers
- **Distributed Training**: DeepSpeed
- **Fine-Tuning**: PEFT (LoRA/QLoRA)
- **API Framework**: FastAPI
- **Caching**: CacheTools, Redis
- **Database**: PostgreSQL
- **Model Serving**: HuggingFace Transformers + DeepSpeed

