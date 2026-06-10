"""
Axon AI — Final Build
"""

import streamlit as st
import pandas as pd
from engine import ask_axon
from utils import fetch_news, validate_csv, get_smart_examples

# ── Page Config ─────────────────────────────────────────────────
st.set_page_config(page_title="Axon AI", page_icon="⚡", layout="wide")

# ── Dark Theme CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp { font-family: 'Inter', sans-serif; background: #0a0a12; }
    #MainMenu, header, footer {visibility: hidden;}
    .block-container { padding: 20px 28px 40px; max-width: 1000px; }
    
    .hero {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.06);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .hero-title { font-size: 26px; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
    .hero-title span { color: #fbbf24; }
    .hero-sub { font-size: 12px; color: rgba(255,255,255,0.45); margin-top: 3px; }
    .pill { display: inline-block; padding: 4px 12px; border-radius: 100px; font-size: 10px; font-weight: 600; }
    .pill-on { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.15); }
    .pill-off { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.35); border: 1px solid rgba(255,255,255,0.08); }
    .hero-meta { font-size: 10px; color: rgba(255,255,255,0.25); margin-top: 6px; }
    
    .m-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 14px 0; }
    .m-card { background: #111119; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 14px; text-align: center; }
    .m-val { font-size: 24px; font-weight: 800; color: #f1f5f9; }
    .m-label { font-size: 9px; font-weight: 600; color: #4b5563; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 3px; }
    .q-bar { height: 4px; background: #1f2937; border-radius: 2px; margin-top: 6px; overflow: hidden; }
    .q-fill { height: 100%; border-radius: 2px; }
    .q-good { background: #10b981; }
    .q-ok { background: #f59e0b; }
    .q-bad { background: #ef4444; }
    
    .news-card {
        background: #111119;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: border-color 0.15s;
    }
    .news-card:hover { border-color: rgba(251,191,36,0.3); }
    .news-topic { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #f59e0b; }
    .news-headline { font-size: 13px; font-weight: 500; color: #e2e8f0; margin-top: 4px; line-height: 1.4; }
    .news-headline a { color: #e2e8f0; text-decoration: none; }
    .news-headline a:hover { color: #fbbf24; }
    .news-source { font-size: 10px; color: #4b5563; margin-top: 4px; }
    
    .stChatMessage { border-radius: 12px !important; }
    
    .stButton > button {
        border-radius: 8px !important; font-size: 11px !important; font-weight: 500 !important;
        border: 1px solid rgba(255,255,255,0.08) !important; background: #111119 !important; color: #94a3b8 !important;
    }
    .stButton > button:hover { border-color: #fbbf24 !important; color: #fbbf24 !important; }
    
    .footer { text-align: center; font-size: 10px; color: #94a3b8; padding: 20px 0 8px; border-top: 1px solid rgba(255,255,255,0.04); margin-top: 30px; }
    .footer strong { color: #e2e8f0; }
    
    @media (max-width: 768px) {
        .block-container { padding: 12px 14px 40px; }
        .hero { padding: 18px 20px; flex-direction: column; align-items: flex-start; gap: 8px; }
        .hero-title { font-size: 22px; }
        .m-grid { grid-template-columns: repeat(2, 1fr); }
        .m-val { font-size: 20px; }
    }
</style>
""", unsafe_allow_html=True)

# ── Session State ───────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "datasets" not in st.session_state:
    st.session_state.datasets = {}
if "news_df" not in st.session_state:
    st.session_state.news_df = fetch_news()
if "auto_insights" not in st.session_state:
    st.session_state.auto_insights = None
if "show_news" not in st.session_state:
    st.session_state.show_news = False
if "cleaning_reports" not in st.session_state:
    st.session_state.cleaning_reports = {}

datasets = st.session_state.datasets
news_df = st.session_state.news_df

# ── Header ──────────────────────────────────────────────────────
n_files = len(datasets)
n_rows = sum(len(d) for d in datasets.values())
pill = "pill-on" if datasets else "pill-off"
pill_txt = "● Live" if datasets else "○ No Data"

st.markdown(f"""
<div class="hero">
    <div>
        <div class="hero-title">⚡ Axon<span>AI</span></div>
        <div class="hero-sub">Upload any dataset. Ask anything. Get real answers.</div>
    </div>
    <div style="text-align:right;">
        <span class="pill {pill}">{pill_txt}</span>
        <div class="hero-meta">{n_files} file{'s' if n_files!=1 else ''} · {n_rows:,} rows · {len(news_df)} news</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Data Stats (only when loaded) ───────────────────────────────
if datasets:
    first_df = list(datasets.values())[0]
    total_cells = first_df.shape[0] * first_df.shape[1]
    null_cells = first_df.isnull().sum().sum()
    qpct = round((1 - null_cells / total_cells) * 100, 1) if total_cells > 0 else 100
    qclass = "q-good" if qpct >= 95 else "q-ok" if qpct >= 80 else "q-bad"
    
    st.markdown(f"""
    <div class="m-grid">
        <div class="m-card"><div class="m-val">{n_rows:,}</div><div class="m-label">Rows</div></div>
        <div class="m-card"><div class="m-val">{sum(len(d.columns) for d in datasets.values())}</div><div class="m-label">Columns</div></div>
        <div class="m-card"><div class="m-val">{len(first_df.select_dtypes(include='number').columns)}</div><div class="m-label">Numeric</div></div>
        <div class="m-card">
            <div class="m-val">{qpct}%</div><div class="m-label">Data Quality</div>
            <div class="q-bar"><div class="q-fill {qclass}" style="width:{qpct}%"></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show cleaning reports
    if st.session_state.cleaning_reports:
        with st.expander("✨ Auto-cleaning report"):
            for fname, actions in st.session_state.cleaning_reports.items():
                if actions:
                    st.markdown(f"**{fname}**")
                    for action in actions:
                        st.markdown(f"• {action}")
                else:
                    st.markdown(f"**{fname}** — already clean ✓")
    
    with st.expander("👀 Preview Data"):
        for name, data in datasets.items():
            st.caption(f"**{name}**")
            st.dataframe(data.head(10), use_container_width=True)
    
    # Auto-Insights
    if st.session_state.auto_insights is None:
        with st.spinner("⚡ Generating insights..."):
            r = ask_axon(
                "Give me exactly 3 key findings from this dataset. Be specific with numbers. One line each, start each with an emoji.",
                datasets=datasets, news_df=news_df
            )
            st.session_state.auto_insights = r["answer"]
    
    if st.session_state.auto_insights:
        st.markdown("##### ⚡ Quick Insights")
        st.markdown(st.session_state.auto_insights)

# ── Action Buttons ──────────────────────────────────────────────
st.markdown("")
bc1, bc2, bc3, bc4 = st.columns(4)
with bc1:
    if st.button("📰 Market News", use_container_width=True):
        st.session_state.show_news = not st.session_state.show_news
with bc2:
    if datasets:
        if st.button("🔍 Find Anomalies", use_container_width=True):
            st.session_state["pending_q"] = "Find any anomalies, outliers, or unusual patterns in this data. Be specific."
with bc3:
    if datasets:
        if st.button("📧 Draft Report", use_container_width=True):
            st.session_state["pending_q"] = "Draft a professional executive summary report of the key findings from this dataset."
with bc4:
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ── News Panel ──────────────────────────────────────────────────
if st.session_state.show_news and len(news_df) > 0:
    st.markdown("##### 📰 Live News — click to read")
    ncols = st.columns(2)
    for i, (_, row) in enumerate(news_df.head(10).iterrows()):
        with ncols[i % 2]:
            link = row.get('link', '#')
            st.markdown(f"""
            <div class="news-card">
                <div class="news-topic">{row['topic']}</div>
                <div class="news-headline"><a href="{link}" target="_blank">{row['title']}</a></div>
                <div class="news-source">{row['source']}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Smart Examples ──────────────────────────────────────────────
if datasets:
    st.markdown("")
    st.markdown("##### 💡 Try:")
    examples = get_smart_examples(list(datasets.values())[0])
    ecols = st.columns(3)
    for i, ex in enumerate(examples[:6]):
        with ecols[i % 3]:
            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state["pending_q"] = ex

st.divider()

# ── Chat ────────────────────────────────────────────────────────

if not datasets:
    st.markdown("#### 💬 Chat")
    st.markdown("📎 **Attach a CSV, Excel, or JSON file to start**")
    uploaded = st.file_uploader(
        "drop_file", type=["csv", "xlsx", "xls", "json"], accept_multiple_files=True, label_visibility="collapsed"
    )
    if uploaded:
        for f in uploaded:
            if f.name not in st.session_state.datasets:
                df, error, actions = validate_csv(f)
                if error:
                    st.error(f"❌ {f.name}: {error}")
                else:
                    st.session_state.datasets[f.name] = df
                    st.session_state.cleaning_reports[f.name] = actions
                    st.session_state.auto_insights = None
                    if actions:
                        st.success(f"✨ {f.name} loaded and cleaned: {', '.join(actions)}")
                    st.rerun()
else:
    with st.expander("📂 Manage uploaded files"):
        for name in list(datasets.keys()):
            fc1, fc2 = st.columns([3, 1])
            with fc1:
                st.markdown(f"✅ **{name}** — {len(datasets[name]):,} rows")
            with fc2:
                if st.button("✕", key=f"del_{name}"):
                    del st.session_state.datasets[name]
                    if name in st.session_state.cleaning_reports:
                        del st.session_state.cleaning_reports[name]
                    st.session_state.auto_insights = None
                    st.rerun()
        add_more = st.file_uploader("Add more files", type=["csv", "xlsx", "xls", "json"], accept_multiple_files=True, label_visibility="collapsed")
        if add_more:
            for f in add_more:
                if f.name not in st.session_state.datasets:
                    df, error, actions = validate_csv(f)
                    if not error:
                        st.session_state.datasets[f.name] = df
                        st.session_state.cleaning_reports[f.name] = actions
                        st.session_state.auto_insights = None
                        if actions:
                            st.success(f"✨ {f.name} cleaned: {', '.join(actions)}")
                        st.rerun()
    st.markdown("#### 💬 Chat")

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "⚡"):
        st.markdown(msg["content"])
        if msg.get("chart_fig"):
            st.pyplot(msg["chart_fig"])

st.markdown('<div class="footer">Built by <strong>Tejas Sonavane</strong> · MS Business Analytics, Syracuse University · RAG · Llama 3.3 · Groq · Python</div>', unsafe_allow_html=True)

# Input — always render chat input
chat_input_value = st.chat_input("Ask anything about your data...")

if "pending_q" in st.session_state:
    prompt = st.session_state.pop("pending_q")
elif chat_input_value:
    prompt = chat_input_value
else:
    prompt = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="⚡"):
        if not datasets:
            if len(news_df) > 0:
                with st.spinner("⚡ Thinking..."):
                    result = ask_axon(
                        prompt,
                        datasets={"info": pd.DataFrame({"status": ["No CSV uploaded yet."]})},
                        news_df=news_df,
                        chat_history=st.session_state.messages[:-1]
                    )
                st.markdown(result["answer"])
                st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
            else:
                msg = "📂 Attach a CSV above to get started."
                st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
        else:
            with st.spinner("⚡ Analyzing..."):
                result = ask_axon(
                    prompt, datasets=datasets, news_df=news_df,
                    chat_history=st.session_state.messages[:-1]
                )
            st.markdown(result["answer"])
            if result["chart_fig"]:
                st.pyplot(result["chart_fig"])
            elif result["has_code"] and not result["chart_fig"]:
                st.info("📊 Chart couldn't render. Try rephrasing.")
            st.session_state.messages.append({
                "role": "assistant", "content": result["answer"],
                "chart_fig": result.get("chart_fig")
            })