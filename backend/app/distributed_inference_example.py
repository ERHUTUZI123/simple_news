# Distributed Inference Example with DeepSpeed

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import deepspeed

MODEL_NAME = "bigscience/bloom-7b1"

if __name__ == "__main__":
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16, device_map="auto")
    # Initialize DeepSpeed inference
    model = deepspeed.init_inference(model, mp_size=2, dtype=torch.float16, replace_method="auto")
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=0)
    article = "Your news article text here."
    summary = summarizer(article, max_length=128, min_length=32, do_sample=False)[0]["summary_text"]
    print("Summary:", summary)
