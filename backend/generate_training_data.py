"""
generate_training_data.py

Script to programmatically generate ~24K article-summary pairs for fine-tuning.
This creates the training dataset used for parameter-efficient fine-tuning of the 7B model.
"""
import json
import os
from typing import List, Dict
from news.fetch_news import fetch_from_rss
from news.summarize import summarize_news
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_training_pairs(num_pairs: int = 24000, output_path: str = "./data/article_summary_pairs.jsonl"):
    """
    Generate article-summary pairs from RSS feeds.
    
    Args:
        num_pairs: Target number of pairs to generate (~24K)
        output_path: Output file path for JSONL format
    """
    logger.info(f"Generating {num_pairs} article-summary pairs...")
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    pairs = []
    fetched_articles = []
    
    # Fetch articles from RSS feeds
    logger.info("Fetching articles from RSS feeds...")
    for _ in tqdm(range(num_pairs // 100 + 1), desc="Fetching batches"):
        try:
            articles = fetch_from_rss()
            fetched_articles.extend(articles)
            if len(fetched_articles) >= num_pairs:
                break
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            continue
    
    # Generate summaries for each article
    logger.info("Generating summaries...")
    for article in tqdm(fetched_articles[:num_pairs], desc="Generating summaries"):
        try:
            article_text = article.get("content", article.get("summary", ""))
            if not article_text or len(article_text) < 100:
                continue
            
            # Generate both brief and detailed summaries
            result = summarize_news(article_text, summary_type="detailed")
            summary = result.get("summary", "")
            
            if summary and len(summary) > 50:
                pairs.append({
                    "article": article_text[:2000],  # Limit article length
                    "summary": summary,
                    "source": article.get("source", "unknown"),
                    "title": article.get("title", "")[:200]
                })
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            continue
    
    # Save to JSONL format
    logger.info(f"Saving {len(pairs)} pairs to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')
    
    logger.info(f"Successfully generated {len(pairs)} article-summary pairs")
    return len(pairs)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate training data for fine-tuning")
    parser.add_argument("--num-pairs", type=int, default=24000, help="Number of pairs to generate")
    parser.add_argument("--output", type=str, default="./data/article_summary_pairs.jsonl", help="Output file path")
    args = parser.parse_args()
    
    generate_training_pairs(args.num_pairs, args.output)

