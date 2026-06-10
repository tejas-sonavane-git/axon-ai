# ⚡ Axon AI — Conversational Data Analytics Platform

**Upload any dataset. Ask anything. Get real answers.**

Axon AI is a RAG-powered analytics assistant that lets users upload CSV data and interact with it through natural language. Built with a strict anti-hallucination architecture — every answer is grounded in actual data, never fabricated.

## 🎯 What It Does

| Capability | Description |
|-----------|-------------|
| **Data Q&A** | Ask questions in plain English, get answers with exact numbers from your data |
| **Auto Visualization** | AI generates and renders matplotlib charts inline |
| **Anomaly Detection** | Statistically flags outliers and unusual patterns |
| **Live News Integration** | Connects real-time news feeds to your business context |
| **Report Drafting** | Generates professional emails and summaries referencing real data points |
| **Sentiment Analysis** | Classifies sentiment in text columns with reasoning |
| **Conversation Memory** | Multi-turn context — follow-up questions work naturally |
| **Multi-File Support** | Upload multiple CSVs, AI cross-references them |

## 🏗️ Architecture

```
User Question
    ↓
┌─────────────────────────┐
│  RETRIEVAL LAYER        │
│  • Search uploaded CSVs  │
│  • Column type analysis  │
│  • Statistical summary   │
│  • Live news fetch (RSS) │
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│  PROMPT ENGINEERING     │
│  • System rules (no     │
│    hallucination)        │
│  • Data context injection│
│  • Chat history (memory) │
│  • Smart formatting rules│
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│  LLM (Groq/Llama 3.3)  │
│  • Generates answer      │
│  • Optionally writes     │
│    Python chart code     │
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│  POST-PROCESSING        │
│  • Code extraction       │
│  • Safe chart execution  │
│  • Error handling        │
└──────────┬──────────────┘
           ↓
    User sees answer + chart
```

## 🛡️ Anti-Hallucination Design

This is the core engineering decision. The AI **cannot** make up data because:

1. **Data isolation**: Only uploaded CSV data is sent to the LLM — no external knowledge used for factual claims
2. **Strict system prompt**: The AI is instructed to say "not in the dataset" rather than guess
3. **Column-level context**: The AI receives statistical summaries (min, max, mean, unique values) so it understands data boundaries
4. **No training on user data**: Uses inference-only API calls — data never leaves the session

## 🛠️ Tech Stack

- **Python 3.10+** — Core application logic
- **Streamlit** — Web interface with mobile-responsive design
- **Groq API** — LLM inference (Llama 3.3 70B) — sub-second response times
- **pandas** — Data processing and analysis
- **matplotlib** — Chart generation from AI-written code
- **feedparser** — Live RSS news integration
- **RAG (Retrieval Augmented Generation)** — Architecture pattern for grounded AI responses

## 📁 Project Structure

```
axon-ai/
├── app.py          ← Streamlit UI (mobile-first, responsive)
├── engine.py       ← AI engine (RAG pipeline, code execution, memory)
├── utils.py        ← Helpers (news fetch, data validation, smart examples)
├── config.py       ← Settings (API keys, model params, feed URLs)
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/axon-ai.git
cd axon-ai
pip install -r requirements.txt
# Add your Groq API key in config.py
streamlit run app.py
```

## 📋 Requirements

```
streamlit
groq
pandas
matplotlib
feedparser
numpy
```

## 💡 Design Decisions

**Why RAG over fine-tuning?**
Fine-tuning would lock the model to specific data. RAG lets users upload ANY dataset and get instant analysis — no retraining needed.

**Why Groq over OpenAI?**
Groq runs Llama 3.3 70B with sub-second latency on their LPU hardware. For an interactive chat experience, speed matters more than marginal quality differences. Also free tier available.

**Why execute AI-generated code?**
Asking an LLM to "describe a chart" is useless. Having it write real matplotlib code that actually renders — that's the difference between a chatbot and an analytics tool.

**Why conversation memory?**
Without memory, every question is isolated. With it, users can say "break that down by region" or "now compare it with last quarter" — natural analytical workflow.

## 👤 Author

**Tejas Sonavane**  
MS Business Analytics (2026) | Martin J. Whitman School of Management  
Syracuse University | tsonavan@syr.edu

---

*Built as a demonstration of applied GenAI in business analytics — combining RAG architecture, prompt engineering, and practical data science into a production-ready tool.*
