import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Tuple

# Load model and tokenizer once
MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Stricter list of distress keywords (only severe/urgent cases)
DISTRESS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "hopeless", "can't go on", "no way out",
    "lost hope", "want to die", "wanna die", "wish I was dead", "give up", "self harm",
    "hurt myself", "depressed", "crisis"
]

# Whitelist of crop-related terms (if present, never trigger distress)
CROP_TERMS = [
    "crop", "plant", "tree", "soil", "fruit", "leaf", "leaves", "flower", "flowers", "field", "farm", "seed", "root", "stem", "disease", "pest", "harvest", "yield", "fertilizer", "irrigation"
]

def is_distress_message(text: str) -> Tuple[bool, str]:
    """
    Returns (is_distress, reason). Reason is a string explaining why distress was detected.
    """
    lowered = text.lower()
    # Whitelist: if crop-related term is present, never trigger distress
    for term in CROP_TERMS:
        if term in lowered:
            return False, ""
    # Keyword check (case-insensitive, stricter)
    for kw in DISTRESS_KEYWORDS:
        if kw in lowered:
            return True, f"Keyword detected: '{kw}'"
    # Sentiment analysis (very strict)
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
        scores = outputs.logits.softmax(dim=1).squeeze()
        negative_score = scores[0].item()
        positive_score = scores[1].item()
    if negative_score > 0.99 and negative_score > positive_score:
        return True, f"High negative sentiment ({negative_score:.2f})"
    return False, ""
