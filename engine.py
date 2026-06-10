"""
Axon AI — Core Engine
RAG pipeline, conversation memory, and code execution
"""

import pandas as pd
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import sys
import traceback
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME, MAX_TOKENS, MAX_DATA_ROWS, MAX_CHAT_HISTORY

client = Groq(api_key=GROQ_API_KEY)


def get_column_summary(df):
    """Generate a smart summary of each column for the AI."""
    lines = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        if df[col].dtype in ["int64", "float64"]:
            lines.append(
                f"  {col} ({dtype}): min={df[col].min()}, max={df[col].max()}, "
                f"mean={df[col].mean():.2f}, median={df[col].median():.2f}, nulls={df[col].isnull().sum()}"
            )
        else:
            unique = df[col].nunique()
            top_vals = ", ".join(map(str, df[col].dropna().unique()[:6]))
            lines.append(f"  {col} ({dtype}): {unique} unique — [{top_vals}]")
    return "\n".join(lines)


def build_data_context(datasets):
    """Build a combined data context string from multiple datasets."""
    parts = []
    for name, df in datasets.items():
        if len(df) > MAX_DATA_ROWS:
            data_str = df.head(MAX_DATA_ROWS).to_string(index=False)
            note = f"(Showing {MAX_DATA_ROWS} of {len(df)} rows)"
        else:
            data_str = df.to_string(index=False)
            note = f"({len(df)} rows)"
        
        col_summary = get_column_summary(df)
        parts.append(f"=== DATASET: {name} {note} ===\nCOLUMNS:\n{col_summary}\n\nDATA:\n{data_str}")
    
    return "\n\n".join(parts)


def build_news_context(news_df):
    """Build news context string."""
    if news_df is None or len(news_df) == 0:
        return ""
    return f"\n=== LIVE NEWS ({len(news_df)} articles) ===\n{news_df[['topic','title','source']].to_string(index=False)}"


SYSTEM_PROMPT = """You are Axon AI — an elite data analyst and business intelligence assistant.

CORE RULES (NEVER BREAK THESE):
1. Answer ONLY from the data provided. Never invent numbers, names, or facts.
2. If the answer is not in the data, say: "That's not in the current dataset."
3. Use exact values — SKUs, prices, names, dates — from the data.
4. Be concise. No filler. Every sentence should add value.

CAPABILITIES:
- Data Analysis: Answer questions using exact numbers from the dataset.
- Visualization: When user asks for a chart/graph/plot, respond with ONLY a Python code block using pandas and matplotlib. The code must:
  - Start with ```python
  - Use the variable `df` which contains the uploaded data
  - End with plt.tight_layout() and plt.savefig('chart.png', dpi=150, bbox_inches='tight')
  - Use clean styling: plt.style.use('seaborn-v0_8-whitegrid')
  - NEVER call plt.show()
  - If multiple datasets, they are available as df_1, df_2, etc.
- Anomaly Detection: Flag statistical outliers (>2 std from mean) and unusual patterns.
- Recommendations: Suggest actions based on data patterns. Always cite the specific data point.
- Communication: Draft emails, reports, and summaries referencing real data points.
- News Analysis: Connect news headlines to business data and explain potential impact.
- Sentiment Analysis: Analyze sentiment in text columns. Classify as positive/negative/neutral with reasoning.

FORMATTING:
- Use **bold** for key numbers and product names.
- Use bullet points for lists.
- Keep answers under 300 words unless user asks for detail.
- When showing rankings, use numbered lists with the actual values.

CONVERSATION:
- You have memory of previous messages. Use it.
- If user says "tell me more" or "explain that", refer to your last answer.
- If user says "compare with" or "what about", connect to prior context."""


def ask_axon(question, datasets, news_df=None, chat_history=None):
    """
    Main function: Ask Axon AI a question.
    """
    
    data_context = build_data_context(datasets)
    news_context = build_news_context(news_df)
    
    user_prompt = f"""{data_context}
{news_context}

Question: {question}"""
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if chat_history:
        recent = chat_history[-MAX_CHAT_HISTORY:]
        for msg in recent:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_prompt})
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            messages=messages
        )
        answer = response.choices[0].message.content
    except Exception as e:
        return {
            "answer": f"⚠️ AI request failed: {str(e)[:100]}. Try again.",
            "has_code": False,
            "code": None,
            "chart_fig": None
        }
    
    has_code = "```python" in answer
    code = None
    chart_fig = None
    
    if has_code:
        code = extract_code(answer)
        if code:
            chart_fig = execute_chart_code(code, datasets)
            if chart_fig:
                answer = re.sub(r'```python.*?```', '', answer, flags=re.DOTALL).strip()
                if not answer:
                    answer = "Here's your chart:"
    
    return {
        "answer": answer,
        "has_code": has_code,
        "code": code,
        "chart_fig": chart_fig
    }


def extract_code(text):
    """Extract Python code from markdown code blocks."""
    if "```python" not in text:
        return None
    try:
        code = text.split("```python")[1].split("```")[0].strip()
        return code
    except (IndexError, ValueError):
        return None


def execute_chart_code(code, datasets):
    """Safely execute AI-generated chart code and return the figure."""
    try:
        plt.close("all")
        plt.style.use("seaborn-v0_8-whitegrid")
        
        namespace = {"pd": pd, "plt": plt, "np": __import__("numpy")}
        
        dataset_items = list(datasets.items())
        if dataset_items:
            namespace["df"] = dataset_items[0][1]
            for i, (name, data) in enumerate(dataset_items):
                namespace[f"df_{i+1}"] = data
                clean_name = name.replace(".csv", "").replace(" ", "_").replace("-", "_")
                namespace[clean_name] = data
        
        safe_code = code.replace("plt.show()", "")
        exec(safe_code, namespace)
        
        fig = plt.gcf()
        if fig.get_axes():
            return fig
        return None
        
    except Exception as e:
        print(f"Chart execution error: {e}")
        return None