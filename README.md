# Sentiment Analysis - AI/ML Capstone Project

A real-time sentiment analysis system built with a fine-tuned DistilBERT model and a hybrid NLP rules engine for accurate classification of text into Positive, Negative, or Neutral.

## Live Demo

[https://huggingface.co/spaces/sanam1/sentiment-Analysis-AI](https://huggingface.co/spaces/sanam1/sentiment-Analysis-AI)

## Architecture

```
User Input -> Streamlit Dashboard -> FastAPI Backend -> DistilBERT Model + NLP Rules Engine -> Result
```

## Tech Stack

- **Model**: DistilBERT (fine-tuned on 50K IMDB reviews + 5,688 edge cases)
- **Backend**: FastAPI with hybrid inference pipeline
- **Frontend**: Streamlit with custom dark-theme UI
- **Training**: Hugging Face Transformers, PyTorch (trained on Kaggle GPU T4 x2)
- **Deployment**: Docker on Hugging Face Spaces

## Key Features

- Real-time single review analysis with positivity score
- Batch CSV upload and analysis with downloadable results
- Sentiment trend chart with interactive Plotly visualization
- Hybrid NLP rules engine for sarcasm, negation, and neutral detection
- Auto-restarting server architecture

## Training Pipeline

1. **Phase 1**: Baseline training on 5,000 IMDB reviews (3 epochs)
2. **Phase 2**: Edge case mining from 50,000 reviews (sarcasm, negation, mixed sentiment)
3. **Phase 3**: Fine-tuning on 5,688 mined edge cases with low learning rate (1e-5)

## Classification Thresholds

| Sentiment | Positive Score Range |
|-----------|---------------------|
| Positive  | 66% - 100%          |
| Neutral   | 30% - 65%           |
| Negative  | 0% - 29%            |

## How to Run Locally

```bash
pip install -r requirements.txt
python run.py
```

The dashboard will be available at `http://localhost:7860`

## Project Structure

```
aiml/
├── api/
│   └── main.py            # FastAPI backend with inference + NLP rules
├── dashboard/
│   └── app.py             # Streamlit frontend dashboard
├── data/
│   └── sample_reviews.csv # Sample test data
├── model_output/          # Fine-tuned DistilBERT weights (not in repo)
├── run.py                 # Unified server launcher
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker config for Hugging Face Spaces
└── README.md
```
