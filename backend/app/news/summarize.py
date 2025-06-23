import hashlib
import os
import json

CACHE_DIR = "/tmp/news_summary_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def summarize_news(text: str, word_count: int = 70) -> str:
    # 用正文内容做哈希
    key = hashlib.md5(text.encode("utf-8")).hexdigest()
    cache_path = os.path.join(CACHE_DIR, key + ".json")
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)["summary"]

    # ...调用 GPT 生成摘要...
    summary = ... # 你的 GPT 调用
    with open(cache_path, "w") as f:
        json.dump({"summary": summary}, f)
    return summary


