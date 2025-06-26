import hashlib
import os
import json
import openai
from typing import Dict, Any

CACHE_DIR = "/tmp/news_summary_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def summarize_news(text: str, summary_type: str = "brief") -> Dict[str, Any]:
    """
    Generate news summary, supports brief and detailed types
    Returns a dictionary containing summary and structure score
    """
    # Use content and type for hash
    cache_key = f"{text}_{summary_type}"
    key = hashlib.md5(cache_key.encode("utf-8")).hexdigest()
    cache_path = os.path.join(CACHE_DIR, key + ".json")
    
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)

    # Set different prompts based on type
    if summary_type == "brief":
        prompt = f"""
        Please generate a concise summary for the following news article in English. Requirements:
        1. 2-3 sentences, approximately 150-200 characters
        2. Highlight core facts and key information
        3. Use objective and accurate language
        4. Avoid subjective commentary
        5. Write in clear, professional English
        
        News content:
        {text}
        
        Please return only the summary content in English, no other explanations.
        """
        max_tokens = 100
    else:  # detailed
        prompt = f"""
        Please generate a detailed summary for the following news article in English. Requirements:
        1. 420+ characters, 65+ words
        2. Include background information and impact analysis
        3. Clear structure and logical flow
        4. Provide deep insights
        5. Write in clear, professional English
        
        News content:
        {text}
        
        Please return only the summary content in English, no other explanations.
        """
        max_tokens = 300

    try:
        # Call OpenAI API
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip() if response.choices[0].message.content else "Summary generation failed"
        
        # Calculate structure score (simplified version)
        structure_score = calculate_structure_score(summary, summary_type)
        
        result = {
            "summary": summary,
            "structure_score": structure_score
        }
        
        # Cache result
        with open(cache_path, "w") as f:
            json.dump(result, f)
        
        return result
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        # Return default result
        return {
            "summary": "Summary generation failed",
            "structure_score": 3.0
        }

def calculate_structure_score(summary: str, summary_type: str) -> float:
    """
    Calculate structure score for summary (1-5 points)
    Based on length, completeness, logic, etc.
    """
    score = 3.0  # Base score
    
    # Length score
    char_count = len(summary)
    word_count = len(summary.split())
    
    if summary_type == "brief":
        if 150 <= char_count <= 200 and 20 <= word_count <= 30:
            score += 1.0
        elif 100 <= char_count <= 250 and 15 <= word_count <= 35:
            score += 0.5
    else:  # detailed
        if char_count >= 420 and word_count >= 65:
            score += 1.0
        elif char_count >= 300 and word_count >= 50:
            score += 0.5
    
    # Structure completeness score
    if "." in summary and len(summary.split(".")) >= 2:
        score += 0.5
    
    # Keyword coverage score
    important_words = ["because", "therefore", "however", "meanwhile", "additionally", "furthermore", "consequently", "nevertheless", "moreover", "thus"]
    if any(word.lower() in summary.lower() for word in important_words):
        score += 0.5
    
    return min(5.0, max(1.0, score))

def generate_both_summaries(text: str) -> Dict[str, Any]:
    """
    Generate both brief and detailed summaries
    """
    brief_result = summarize_news(text, "brief")
    detailed_result = summarize_news(text, "detailed")
    
    return {
        "brief": brief_result["summary"],
        "detailed": detailed_result["summary"],
        "structure_score": (brief_result["structure_score"] + detailed_result["structure_score"]) / 2
    }


