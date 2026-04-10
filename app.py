import streamlit as st
import pandas as pd

# --- APPLE DARK UI ---
st.set_page_config(page_title="DASA Predictor", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
        background-color: #000000;
        color: #F5F5F7;
    }
    .stApp { background-color: #000000; }
    .apple-card {
        background-color: #1C1C1E;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        border: 1px solid #38383A;
    }
    .inst-text { font-weight: 600; color: #FFFFFF; font-size: 1.1rem; }
    .prog-text { color: #8E8E93; font-size: 0.9rem; margin-top: 4px; }
    .rank-text { 
        display: inline-block; margin-top: 10px;
        color: #0A84FF; font-weight: 600; font-size: 0.85rem;
        background: #2C2C2E; padding: 4px 8px; border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("DASA Predictor")

@st.cache_data
def load_and_clean_data():
    try:
        df = pd.read_csv("dasa_data.csv")
        # Ensure Closing Rank is numeric
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'], errors='coerce')
        # Only keep rows with valid ranks
        df = df.dropna(subset=['Closing Rank'])
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = load_and_clean_data()

if df is not None:
    # --- UI INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        rank_input = st.number_input("Enter Your Rank", min_value=1, value=50000)
    with col2:
        # Strictly limited to the two options you requested
        category = st.selectbox("Select Quota", ["DASA-CIWG", "DASA-Non CIWG"])

    st.divider()

    # --- CROSSCHECK LOGIC ---
    # Filter strictly by category and where user_rank <= Closing Rank
    matches = df[
        (df['Quota'] == category) & 
        (rank_input <= df['Closing Rank'])
    ]
    
    # Sort by Closing Rank (Competitive first)
    matches = matches.sort_values(by='Closing Rank')

    # --- DISPLAY ---
    if matches.empty:
        st.warning(f"No matches found for Rank {rank_input} in {category}.")
    else:
        st.subheader(f"Available Institutes ({len(matches)})")
        for _, row in matches.iterrows():
            st.markdown(f"""
                <div class="apple-card">
                    <div class="inst-text">{row['Institute']}</div>
                    <div class="prog-text">{row['Academic Program Name']}</div>
                    <div class="rank-text">2025 CLOSING RANK: {int(row['Closing Rank']):,}</div>
                </div>
            """, unsafe_allow_html=True)
