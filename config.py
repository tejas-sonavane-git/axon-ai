"""
Axon AI — Configuration
"""
import streamlit as st

# ── API Key ─────────────────────────────────────────────────────
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

# ── Model Settings ──────────────────────────────────────────────
MODEL_NAME = "llama-3.3-70b-versatile"
MAX_TOKENS = 2048
MAX_DATA_ROWS = 150
MAX_CHAT_HISTORY = 6

# ── News Feeds ──────────────────────────────────────────────────
NEWS_FEEDS = {
    "Housing Market": "https://news.google.com/rss/search?q=housing+market+construction&hl=en-US",
    "Window & Door": "https://news.google.com/rss/search?q=window+door+glass+fenestration&hl=en-US",
    "AI & Business": "https://news.google.com/rss/search?q=AI+business+digital+transformation&hl=en-US",
}
NEWS_PER_FEED = 5