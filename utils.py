"""
Axon AI — Utilities
News fetching, data validation, auto-cleaning, helpers
"""

import pandas as pd
from config import NEWS_FEEDS, NEWS_PER_FEED


def fetch_news():
    """Fetch live news from Google RSS feeds. Returns DataFrame."""
    try:
        import feedparser
    except ImportError:
        return pd.DataFrame()
    
    rows = []
    for topic, url in NEWS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:NEWS_PER_FEED]:
                rows.append({
                    "topic": topic,
                    "title": entry.get("title", "No title"),
                    "source": entry.source.title if hasattr(entry, "source") and hasattr(entry.source, "title") else "Unknown",
                    "link": entry.get("link", ""),
                    "published": entry.get("published", "N/A"),
                })
        except Exception:
            continue
    
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def clean_dataframe(df):
    """Auto-clean a DataFrame. Returns (cleaned_df, list_of_actions)."""
    actions = []
    
    # Strip column name whitespace
    if df.columns.astype(str).str.contains(r'^\s|\s$').any():
        df.columns = df.columns.str.strip()
        actions.append("Trimmed whitespace from column names")
    
    # Strip whitespace in string columns
    string_cols = df.select_dtypes(include='object').columns
    if len(string_cols) > 0:
        for col in string_cols:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        actions.append(f"Trimmed whitespace in {len(string_cols)} text columns")
    
    # Drop fully empty rows
    before = len(df)
    df = df.dropna(how='all')
    if len(df) < before:
        actions.append(f"Removed {before - len(df)} empty rows")
    
    # Drop fully empty columns
    before = len(df.columns)
    df = df.dropna(axis=1, how='all')
    if len(df.columns) < before:
        actions.append(f"Removed {before - len(df.columns)} empty columns")
    
    # Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    if len(df) < before:
        actions.append(f"Removed {before - len(df)} duplicate rows")
    
    # Auto-convert object columns to numeric where 90%+ values are numeric
    converted = 0
    for col in df.select_dtypes(include='object').columns:
        try:
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            non_null_ratio = numeric_series.notna().sum() / len(df) if len(df) > 0 else 0
            if non_null_ratio >= 0.9 and df[col].notna().sum() > 0:
                df[col] = numeric_series
                converted += 1
        except Exception:
            continue
    if converted > 0:
        actions.append(f"Auto-converted {converted} columns to numeric")
    
    # Reset index
    df = df.reset_index(drop=True)
    
    return df, actions


def validate_csv(uploaded_file):
    """
    Validate, load, and auto-clean CSV/Excel/JSON. 
    Returns (DataFrame, error_message, cleaning_actions).
    """
    try:
        filename = uploaded_file.name.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        elif filename.endswith('.json'):
            df = pd.read_json(uploaded_file)
        else:
            return None, "Unsupported format. Use CSV, Excel, or JSON.", []
        
        if len(df) == 0:
            return None, "File is empty.", []
        
        if len(df.columns) < 2:
            return None, "File needs at least 2 columns.", []
        
        # Auto-clean
        df, cleaning_actions = clean_dataframe(df)
        
        return df, None, cleaning_actions
        
    except pd.errors.EmptyDataError:
        return None, "File is empty or not valid.", []
    except pd.errors.ParserError:
        return None, "Could not parse file.", []
    except Exception as e:
        return None, f"Error reading file: {str(e)[:100]}", []


def get_smart_examples(df):
    """Generate smart example questions based on the actual data columns."""
    examples = []
    cols = df.columns.tolist()
    num_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols = df.select_dtypes(include="object").columns.tolist()
    
    examples.append("Give me a summary of this dataset")
    
    if num_cols:
        examples.append(f"What are the top 5 items by {num_cols[0]}?")
        if len(num_cols) > 1:
            examples.append(f"Show a bar chart of {num_cols[0]} by {text_cols[0]}" if text_cols else f"Plot {num_cols[0]} distribution")
    
    if text_cols:
        examples.append(f"Break down the data by {text_cols[0]}")
    
    if num_cols:
        examples.append(f"Find any outliers in {num_cols[0]}")
    
    examples.append("Any news that could impact this data?")
    examples.append("Draft a summary report of key findings")
    
    return examples[:6]