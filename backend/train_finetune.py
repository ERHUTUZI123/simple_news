"""
train_finetune.py

Fine-tuning script for 7B-parameter instruction-tuned language model using parameter-efficient 
fine-tuning (PEFT) on ~24K programmatically generated article-summary pairs.

Uses DeepSpeed ZeRO for distributed training and LoRA/QLoRA for parameter-efficient fine-tuning.
"""
import torch
import os
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from transformers import BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset, Dataset
import deepspeed
from typing import Dict, List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MODEL_NAME = os.getenv("BASE_MODEL", "bigscience/bloom-7b1")  # 7B parameter base model
DATASET_PATH = os.getenv("DATASET_PATH", "./data/article_summary_pairs.jsonl")  # ~24K pairs
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./models/finetuned_7b")
NUM_EPOCHS = int(os.getenv("NUM_EPOCHS", "3"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "4"))
GRADIENT_ACCUMULATION_STEPS = int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "8"))

def load_training_data(dataset_path: str) -> Dataset:
    """
    Load ~24K programmatically generated article-summary pairs.
    Expected format: JSONL with 'article' and 'summary' fields.
    """
    logger.info(f"Loading training data from {dataset_path}")
    
    data = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    
    logger.info(f"Loaded {len(data)} article-summary pairs")
    return Dataset.from_list(data)

def format_instruction_prompt(article: str, summary: str = None) -> str:
    """
    Format training data as instruction-following prompts.
    This enables instruction-tuning for better summarization performance.
    """
    if summary:
        return f"""### Instruction:
Summarize the following news article concisely and accurately.

### Article:
{article}

### Summary:
{summary}"""
    else:
        return f"""### Instruction:
Summarize the following news article concisely and accurately.

### Article:
{article}

### Summary:
"""

def preprocess_function(examples: Dict, tokenizer: AutoTokenizer) -> Dict:
    """
    Preprocess training examples into tokenized format.
    """
    instructions = [
        format_instruction_prompt(article, summary)
        for article, summary in zip(examples["article"], examples["summary"])
    ]
    
    # Tokenize
    model_inputs = tokenizer(
        instructions,
        max_length=1024,
        truncation=True,
        padding="max_length"
    )
    
    # Create labels (same as input_ids for causal LM)
    labels = model_inputs["input_ids"].copy()
    model_inputs["labels"] = labels
    
    return model_inputs

def setup_model_for_training(model_name: str, use_4bit: bool = True):
    """
    Setup 7B model with parameter-efficient fine-tuning (LoRA/QLoRA).
    """
    logger.info(f"Loading base model: {model_name}")
    
    # Configure quantization for memory efficiency (QLoRA)
    if use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        model = prepare_model_for_kbit_training(model)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
    
    # Configure LoRA for parameter-efficient fine-tuning
    lora_config = LoraConfig(
        r=16,  # LoRA rank
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # Adjust based on model architecture
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    return model

def main():
    """
    Main training loop with DeepSpeed ZeRO for distributed training.
    """
    logger.info("Starting fine-tuning of 7B parameter model")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load training data (~24K pairs)
    dataset = load_training_data(DATASET_PATH)
    
    # Preprocess data
    logger.info("Preprocessing training data...")
    tokenized_dataset = dataset.map(
        lambda x: preprocess_function(x, tokenizer),
        batched=True,
        remove_columns=dataset.column_names
    )
    
    # Setup model with PEFT
    model = setup_model_for_training(MODEL_NAME, use_4bit=True)
    
    # Training arguments with DeepSpeed support
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_steps=500,
        eval_steps=500,
        warmup_steps=100,
        save_total_limit=3,
        deepspeed=os.getenv("DEEPSPEED_CONFIG", "ds_config.json"),  # DeepSpeed ZeRO config
        report_to="tensorboard",
        run_name=f"7b_finetune_{NUM_EPOCHS}epochs"
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )
    
    # Train
    logger.info("Starting training...")
    trainer.train()
    
    # Save final model
    logger.info(f"Saving fine-tuned model to {OUTPUT_DIR}")
    trainer.save_model()
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    logger.info("Fine-tuning completed!")

if __name__ == "__main__":
    main()

