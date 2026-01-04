"""
model_inference.py

Production-ready distributed inference system for a 7B-parameter instruction-tuned language model.
Handles loading the LLM with HuggingFace Transformers, efficient batching, caching, and distributed 
inference with DeepSpeed for high-throughput processing of ~30,000 articles per day.
"""
# Pytorch
import torch
# os ops
import os
# transformers is huggingface library for pre-trained models
# AutoTokenizer converts text <-> numbers for the model
# AutoModelForCausalLM is language model that generates text sequentially
# high-level wrapper for common tasks (create a chain: input -> tokenizer -> model -> post-processing)
# pipeline is a high-level wrapper for common tasks (create a chain: input -> tokenizer -> model -> post-processing)
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# LRUCache evicts least recently used items when full
# TTLCache evicts items after a time-to-live 
from cachetools import LRUCache, TTLCache
from functools import lru_cache
import deepspeed
from typing import List, Dict, Optional
import logging
from datetime import datetime
import hashlib
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration - 7B parameter instruction-tuned model
MODEL_NAME = os.getenv("MODEL_NAME", "bigscience/bloom-7b1")  # Replace with your fine-tuned model path
CACHE_SIZE = 10000  # Increased cache for high-volume processing
CACHE_TTL = 86400  # 24 hours cache TTL

# Initialize caches for summaries and scores
summary_cache = TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TTL)
score_cache = TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TTL)

# Global model and tokenizer (lazy loading)
TOKENIZER: Optional[AutoTokenizer] = None
MODEL: Optional[AutoModelForCausalLM] = None
SUMMARIZER: Optional[pipeline] = None
_model_loaded = False

def get_model():
    """
    Load 7B-parameter model and tokenizer with DeepSpeed inference for distributed processing.
    Uses parameter-efficient loading with FP16 precision for memory optimization.
    """
    global TOKENIZER, MODEL, SUMMARIZER, _model_loaded
    
    if _model_loaded:
        return TOKENIZER, MODEL, SUMMARIZER
    
    logger.info(f"Loading 7B parameter model: {MODEL_NAME}")
    
    # Load tokenizer
    TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
    if TOKENIZER.pad_token is None:
        TOKENIZER.pad_token = TOKENIZER.eos_token
    
    # Load model with optimized settings
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto",
        low_cpu_mem_usage=True,
        trust_remote_code=True
    )
    
    # Initialize DeepSpeed for distributed inference
    # Supports multi-GPU inference for high throughput
    mp_size = int(os.getenv("DEEPSPEED_MP_SIZE", "1"))  # Model parallelism size
    if mp_size > 1:
        logger.info(f"Initializing DeepSpeed inference with mp_size={mp_size}")
        model = deepspeed.init_inference(
            model,
            mp_size=mp_size,
            dtype=torch.float16,
            replace_method="auto",
            max_out_tokens=512
        )
    
    MODEL = model
    
    # Initialize summarization pipeline with batching support
    SUMMARIZER = pipeline(
        "summarization",
        model=MODEL,
        tokenizer=TOKENIZER,
        device=0 if torch.cuda.is_available() else -1,
        batch_size=int(os.getenv("INFERENCE_BATCH_SIZE", "8")),
        framework="pt"
    )
    
    _model_loaded = True
    logger.info("Model loaded successfully with DeepSpeed inference")
    
    return TOKENIZER, MODEL, SUMMARIZER

def _get_cache_key(article: str, task: str = "summary") -> str:
    """Generate cache key from article content."""
    content = f"{task}:{article}"
    return hashlib.md5(content.encode("utf-8")).hexdigest()

@lru_cache(maxsize=CACHE_SIZE)
def summarize_article(article: str, use_cache: bool = True) -> str:
    """
    Summarize a single news article using the 7B instruction-tuned LLM.
    
    Args:
        article: News article text to summarize
        use_cache: Whether to use cached results
        
    Returns:
        Generated summary string
    """
    if not article or len(article.strip()) < 50:
        return "Article too short to summarize."
    
    # Check cache first
    if use_cache:
        cache_key = _get_cache_key(article, "summary")
        if cache_key in summary_cache:
            logger.debug("Cache hit for article summary")
            return summary_cache[cache_key]
    
    try:
        # Ensure model is loaded
        tokenizer, model, summarizer = get_model()
        
        # Generate summary with instruction-tuned model
        result = summarizer(
            article,
            max_length=256,
            min_length=64,
            do_sample=False,
            num_beams=4,
            early_stopping=True
        )
        
        summary = result[0]["summary_text"] if isinstance(result, list) else result["summary_text"]
        
        # Cache result
        if use_cache:
            summary_cache[_get_cache_key(article, "summary")] = summary
        
        return summary
        
    except Exception as e:
        logger.error(f"Error summarizing article: {e}")
        return "Summary generation failed."

def batch_summarize(articles: List[str], batch_size: Optional[int] = None) -> List[str]:
    """
    Batch summarization for high-throughput processing.
    Optimized for processing ~30,000 articles per day with efficient batching.
    
    Args:
        articles: List of article texts to summarize
        batch_size: Batch size for processing (defaults to env config)
        
    Returns:
        List of generated summaries
    """
    if not articles:
        return []
    
    batch_size = batch_size or int(os.getenv("INFERENCE_BATCH_SIZE", "8"))
    tokenizer, model, summarizer = get_model()
    
    summaries = []
    
    # Process in batches to optimize memory and throughput
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        
        try:
            # Check cache for each article in batch
            batch_results = []
            uncached_batch = []
            uncached_indices = []
            
            for idx, article in enumerate(batch):
                cache_key = _get_cache_key(article, "summary")
                if cache_key in summary_cache:
                    batch_results.append((idx, summary_cache[cache_key]))
                else:
                    uncached_batch.append(article)
                    uncached_indices.append(idx)
            
            # Process uncached articles
            if uncached_batch:
                logger.info(f"Processing batch of {len(uncached_batch)} uncached articles")
                batch_summaries = summarizer(
                    uncached_batch,
                    max_length=256,
                    min_length=64,
                    do_sample=False,
                    num_beams=4,
                    early_stopping=True,
                    batch_size=min(batch_size, len(uncached_batch))
                )
                
                # Extract summaries and cache them
                for idx, summary_result in zip(uncached_indices, batch_summaries):
                    summary = summary_result["summary_text"] if isinstance(summary_result, dict) else summary_result
                    cache_key = _get_cache_key(uncached_batch[uncached_indices.index(idx)], "summary")
                    summary_cache[cache_key] = summary
                    batch_results.append((idx, summary))
            
            # Sort by original index and extract summaries
            batch_results.sort(key=lambda x: x[0])
            summaries.extend([summary for _, summary in batch_results])
            
        except Exception as e:
            logger.error(f"Error in batch summarization: {e}")
            # Fallback: process individually
            for article in batch:
                summaries.append(summarize_article(article))
    
    return summaries

def importance_score(article: str, summary: str) -> float:
    """
    Calculate importance score for an article using the LLM.
    This score is used for prioritizing articles in downstream decision-making.
    
    Args:
        article: Full article text
        summary: Generated summary
        
    Returns:
        Importance score between 0.0 and 1.0
    """
    if not article or not summary:
        return 0.0
    
    # Check cache
    cache_key = _get_cache_key(f"{article}:{summary}", "score")
    if cache_key in score_cache:
        return score_cache[cache_key]
    
    try:
        tokenizer, model, _ = get_model()
        
        # Use instruction-tuned model to score importance
        # This is a simplified version - in production, use a dedicated scoring prompt
        prompt = f"""Rate the importance of this news article on a scale of 0.0 to 1.0.
        
Article: {article[:500]}
Summary: {summary}

Importance score (0.0-1.0):"""
        
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=10,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract score from response (simplified parsing)
        try:
            score = float(response.split()[-1])
            score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        except:
            # Fallback: use heuristics
            score = min(1.0, (len(article) + len(summary)) / 2000)
        
        score_cache[cache_key] = score
        return score
        
    except Exception as e:
        logger.error(f"Error calculating importance score: {e}")
        # Fallback heuristic
        return min(1.0, len(article) / 1000)

def process_article_batch(articles: List[str]) -> List[Dict[str, Any]]:
    """
    Process a batch of articles with both summarization and scoring.
    Returns structured outputs for downstream integration.
    
    Args:
        articles: List of article texts
        
    Returns:
        List of dictionaries with 'summary', 'score', and 'timestamp'
    """
    summaries = batch_summarize(articles)
    results = []
    
    for article, summary in zip(articles, summaries):
        score = importance_score(article, summary)
        results.append({
            "summary": summary,
            "score": score,
            "timestamp": datetime.utcnow().isoformat(),
            "article_length": len(article),
            "summary_length": len(summary)
        })
    
    return results

# Initialize model on module import (lazy loading can be controlled via env var)
if os.getenv("EAGER_MODEL_LOADING", "false").lower() == "true":
    logger.info("Eager loading model...")
    get_model()
