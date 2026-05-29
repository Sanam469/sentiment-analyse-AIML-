import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Sentiment Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #0a0a0a;
    }

    [data-testid="stSidebarCollapsedControl"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    #MainMenu { display: none; }
    footer { display: none; }
    header { display: none; }

    .dash-heading {
        font-size: 2.4rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -1px;
        margin-bottom: 0.1rem;
    }
    .dash-heading span {
        color: #f97316;
    }
    .dash-sub {
        color: #666;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    .count-card {
        background: #141414;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
    }
    .count-card .num {
        font-size: 2.2rem;
        font-weight: 800;
        color: #fff;
    }
    .count-card .lbl {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #555;
        margin-top: 0.2rem;
        white-space: nowrap;
    }
    .count-card.pos .num { color: #22c55e; }
    .count-card.neg .num { color: #ef4444; }
    .count-card.neu .num { color: #f97316; }
    .count-card.pos { border-left: 4px solid #22c55e; }
    .count-card.neg { border-left: 4px solid #ef4444; }
    .count-card.neu { border-left: 4px solid #f97316; }
    .count-card.total { border-left: 4px solid #f97316; }

    .result-tag {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
    }
    .result-tag.Positive { background: rgba(34,197,94,0.15); color: #22c55e; }
    .result-tag.Negative { background: rgba(239,68,68,0.15); color: #ef4444; }
    .result-tag.Neutral  { background: rgba(249,115,22,0.15); color: #f97316; }

    .review-row {
        background: #141414;
        border: 1px solid #222;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .review-text {
        color: #ccc;
        font-size: 0.9rem;
        flex: 1;
        margin-right: 1rem;
    }
    .review-conf {
        color: #555;
        font-size: 0.8rem;
        margin-right: 1rem;
        white-space: nowrap;
    }

    .section-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #555;
        margin-bottom: 0.8rem;
        margin-top: 1.5rem;
    }

    textarea {
        background: #141414 !important;
        color: #eee !important;
        border: 2px solid #222 !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
    }
    textarea:focus {
        border-color: #f97316 !important;
        box-shadow: 0 0 0 2px rgba(249,115,22,0.2) !important;
    }
    textarea::placeholder {
        color: #444 !important;
    }

    .stButton > button {
        background: #f97316;
        color: #000;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #fb923c;
        color: #000;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 2px solid #1a1a1a; }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #555;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 10px 24px;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
    }
    .stTabs [aria-selected="true"] {
        color: #fff !important;
        border-bottom: 2px solid #f97316 !important;
        background: transparent !important;
    }

    hr { border-color: #1a1a1a !important; }

    [data-testid="stFileUploader"] {
        background: #141414;
        border-radius: 10px;
        padding: 1rem;
    }

    [data-testid="stFileUploader"] button span {
        display: none !important;
    }
    [data-testid="stFileUploader"] button::after {
        content: "Browse CSV";
        display: block;
        color: #000;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stFileUploader"] button {
        background: #f97316 !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    p, span, label, .stMarkdown {
        color: #ccc;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000/predict"

def get_prediction(text):
    try:
        response = requests.post(API_URL, json={"text": text}, timeout=10)
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "API is not running! Start the API server first."}

if "history" not in st.session_state:
    st.session_state.history = []

st.markdown("""
<div style="padding: 1rem 0 0.5rem 0;">
    <div class="dash-heading">Sentiment <span>Analysis</span></div>
    <div class="dash-sub">Fine-tuned DistilBERT  |  Real-time classification</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["LIVE ANALYSIS", "BATCH UPLOAD"])

with tab1:
    left_col, right_col = st.columns([3, 5], gap="large")

    with right_col:
        st.markdown('<div class="section-label">Enter Review</div>', unsafe_allow_html=True)
        user_text = st.text_area(
            "review_input",
            height=100,
            placeholder="Type any product review, comment, or feedback here...",
            label_visibility="collapsed",
        )
        analyze_btn = st.button("Analyze", use_container_width=True)

        if analyze_btn and user_text.strip():
            with st.spinner("Analyzing..."):
                result = get_prediction(user_text.strip())

            if "error" in result:
                st.error(result["error"])
            else:
                sentiment = result["sentiment"]
                confidence = result["confidence"]

                st.markdown(f"""
                <div style="background:#141414; border:1px solid #222; border-radius:12px; padding:1.2rem; margin-top:0.8rem; display:flex; align-items:center; justify-content:space-between;">
                    <span class="result-tag {sentiment}">{sentiment}</span>
                    <div style="text-align:right;">
                        <span style="color:#22c55e; font-weight:600; font-size:0.85rem;">+{result['positive_score']}%</span>
                        <span style="color:#333; margin:0 0.3rem;">|</span>
                        <span style="color:#ef4444; font-weight:600; font-size:0.85rem;">-{result['negative_score']}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.session_state.history.append({
                    "text": user_text.strip()[:100] + ("..." if len(user_text.strip()) > 100 else ""),
                    "sentiment": sentiment,
                    "confidence": confidence,
                    "positive_score": result["positive_score"],
                    "negative_score": result["negative_score"],
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                })

        elif analyze_btn:
            st.warning("Please enter some text first.")

        if len(st.session_state.history) > 0:
            st.markdown('<div class="section-label">Review History</div>', unsafe_allow_html=True)
            for item in reversed(st.session_state.history):
                st.markdown(f"""
                <div class="review-row">
                    <div class="review-text">{item['text']}</div>
                    <span class="result-tag {item['sentiment']}">{item['sentiment']}</span>
                </div>
                """, unsafe_allow_html=True)

    with left_col:
        if len(st.session_state.history) > 0:
            history_df = pd.DataFrame(st.session_state.history)
            total = len(history_df)
            pos_count = len(history_df[history_df["sentiment"] == "Positive"])
            neg_count = len(history_df[history_df["sentiment"] == "Negative"])
            neu_count = len(history_df[history_df["sentiment"] == "Neutral"])

            st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="count-card total"><div class="num">{total}</div><div class="lbl">Total</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="count-card pos"><div class="num">{pos_count}</div><div class="lbl">Positive</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="count-card neg"><div class="num">{neg_count}</div><div class="lbl">Negative</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="count-card neu"><div class="num">{neu_count}</div><div class="lbl">Neutral</div></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-label">Sentiment Trend</div>', unsafe_allow_html=True)

            history_df = history_df.sort_values("timestamp")

            color_map = {"Positive": "#22c55e", "Negative": "#ef4444", "Neutral": "#f97316"}

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=history_df["timestamp"],
                y=history_df["positive_score"],
                mode="lines+markers",
                name="Trend",
                line=dict(color="#f97316", width=2.5),
                marker=dict(
                    size=9,
                    color=history_df["sentiment"].map(color_map),
                    line=dict(color="#ffffff", width=1)
                ),
                hovertemplate="<b>%{text}</b><br>Positivity: %{y}%<extra></extra>",
                text=history_df["text"],
            ))

            fig.update_layout(
                height=380,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor="#0a0a0a",
                paper_bgcolor="#0a0a0a",
                font=dict(family="Inter", color="#ccc", size=12),
                xaxis=dict(
                    showgrid=False,
                    title="",
                    tickfont=dict(color="#555"),
                ),
                yaxis=dict(
                    range=[0, 105],
                    title="Positivity %",
                    gridcolor="#1a1a1a",
                    tickfont=dict(color="#555"),
                    ticksuffix="%",
                    title_font=dict(color="#555", size=11),
                ),
                showlegend=False,
                hovermode="x unified",
            )

            st.plotly_chart(fig, use_container_width=True)

            if st.button("Clear History", use_container_width=True):
                st.session_state.history = []
                st.rerun()
        else:
            st.markdown("""
            <div style="background:#141414; border:1px solid #222; border-radius:14px; padding:3rem 2rem; text-align:center; margin-top:2rem;">
                <div style="font-size:2rem; color:#333; margin-bottom:0.5rem;">&#9680;</div>
                <div style="color:#444; font-size:0.9rem;">Analyze a few reviews to see<br>the sentiment trend chart here</div>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown("CSV should have a column named **text** or **review**.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        text_column = None
        for col in df.columns:
            if col.lower() in ["text", "review", "reviews", "comment", "feedback"]:
                text_column = col
                break

        if text_column is None:
            st.error("No text column found. Name your column 'text' or 'review'.")
        else:
            st.markdown(f"Found **{len(df)} reviews** in column `{text_column}`")

            if st.button("Analyze All", use_container_width=True):
                results = []
                progress = st.progress(0, text="Analyzing...")

                for i, row in df.iterrows():
                    text = str(row[text_column])
                    if text.strip():
                        result = get_prediction(text)
                        if "error" not in result:
                            results.append({
                                "Review": text[:120],
                                "Sentiment": result["sentiment"],
                                "Confidence": result["confidence"],
                                "Pos %": result["positive_score"],
                                "Neg %": result["negative_score"],
                            })
                    progress.progress((i + 1) / len(df), text=f"Review {i + 1} / {len(df)}")

                progress.empty()

                if results:
                    rdf = pd.DataFrame(results)

                    st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)
                    bc1, bc2, bc3, bc4 = st.columns(4)
                    with bc1:
                        st.markdown(f'<div class="count-card total"><div class="num">{len(rdf)}</div><div class="lbl">Total</div></div>', unsafe_allow_html=True)
                    with bc2:
                        st.markdown(f'<div class="count-card pos"><div class="num">{len(rdf[rdf["Sentiment"]=="Positive"])}</div><div class="lbl">Positive</div></div>', unsafe_allow_html=True)
                    with bc3:
                        st.markdown(f'<div class="count-card neg"><div class="num">{len(rdf[rdf["Sentiment"]=="Negative"])}</div><div class="lbl">Negative</div></div>', unsafe_allow_html=True)
                    with bc4:
                        st.markdown(f'<div class="count-card neu"><div class="num">{len(rdf[rdf["Sentiment"]=="Neutral"])}</div><div class="lbl">Neutral</div></div>', unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    counts = rdf["Sentiment"].value_counts().reset_index()
                    counts.columns = ["Sentiment", "Count"]
                    cmap = {"Positive": "#22c55e", "Negative": "#ef4444", "Neutral": "#f97316"}

                    fig_bar = go.Figure(data=[
                        go.Bar(
                            x=counts["Sentiment"],
                            y=counts["Count"],
                            marker_color=[cmap.get(s, "#ccc") for s in counts["Sentiment"]],
                            marker_line_width=0,
                        )
                    ])
                    fig_bar.update_layout(
                        height=300,
                        margin=dict(l=0, r=0, t=10, b=0),
                        plot_bgcolor="#0a0a0a",
                        paper_bgcolor="#0a0a0a",
                        font=dict(family="Inter", color="#ccc"),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(gridcolor="#1a1a1a"),
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                    st.dataframe(rdf, use_container_width=True, hide_index=True)

                    st.download_button(
                        label="Download Results CSV",
                        data=rdf.to_csv(index=False),
                        file_name="sentiment_results.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
