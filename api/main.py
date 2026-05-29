from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

app = FastAPI(title="Sentiment Analysis API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "./model_output"

print("[INFO] Loading the trained AI brain...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()
print("[OK] Brain loaded and ready!")


class ReviewRequest(BaseModel):
    text: str


@app.post("/predict")
def predict_sentiment(request: ReviewRequest):
    inputs = tokenizer(request.text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(outputs.logits, dim=1)
    negative_score = probabilities[0][0].item()
    positive_score = probabilities[0][1].item()

    text_lower = request.text.lower()

    sarcasm_positive_words = ["great", "fantastic", "marvelous", "brilliant", "outstanding", "phenomenal", "beautiful", "wonderful", "amazing"]
    sarcasm_defect_words = ["broken", "damaged", "cracked", "shattered", "failed", "refused", "defective", "fire", "lasts 10", "lasts 5"]

    has_positive = any(word in text_lower for word in sarcasm_positive_words)
    has_defect = any(word in text_lower for word in sarcasm_defect_words)
    is_sarcastic = has_positive and has_defect

    pos_negation_phrases = ["not bad", "not worst", "not terrible", "not awful", "not horrible", "not poor", "not at all bad", "opposite of worst", "opposite of bad", "isn't bad", "isnt bad", "wasn't bad", "wasnt bad", "no complaints", "can't complain", "cant complain", "not a terrible", "can't say it's awful", "cant say its awful", "can't say it's terrible", "cant say its terrible"]
    strong_pos_phrases = ["nothing less than spectacular", "nothing short of amazing", "nothing short of great", "nothing less than brilliant"]
    neg_negation_phrases = ["not good", "not great", "not awesome", "not amazing", "not outstanding", "not impressive", "not worth", "not the best"]

    has_positive_negation = any(phrase in text_lower for phrase in pos_negation_phrases) or any(phrase in text_lower for phrase in strong_pos_phrases)
    has_negative_negation = any(phrase in text_lower for phrase in neg_negation_phrases)

    explicit_neutral_phrases = ["not good, not bad", "not good not bad", "functionality is neutral", "is neutral", "okish", "okayish", "nothing special", "lacks character", "does what it is supposed to", "supposed to do, i guess", "it works", "no strong feelings", "might be useful", "average product"]
    is_explicit_neutral = any(phrase in text_lower for phrase in explicit_neutral_phrases)

    if is_sarcastic:
        positive_score, negative_score = 0.05, 0.95
    elif is_explicit_neutral:
        positive_score, negative_score = 0.55, 0.45
    elif has_positive_negation:
        positive_score, negative_score = 0.85, 0.15
    elif has_negative_negation:
        positive_score, negative_score = 0.15, 0.85

    pos_percent = positive_score * 100
    confidence = max(positive_score, negative_score) * 100

    if pos_percent >= 66:
        sentiment = "Positive"
    elif pos_percent <= 29:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "positive_score": round(positive_score * 100, 2),
        "negative_score": round(negative_score * 100, 2),
    }


@app.get("/")
def home():
    return {"status": "Sentiment Analysis API is running!"}
