import streamlit as st
import pandas as pd

# --- ENHANCED APPLE PRO UI ---
st.set_page_config(page_title="DASA 2026 Predictor", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Base Theme */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #000000;
        color: #F5F5F7;
    }
    
    .stApp {
        background: radial-gradient(circle at top center, #1c1c1e 0%, #000000 100%);
    }

    /* Header Styling */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        background: linear-gradient(180deg, #FFFFFF 0%, #A1A1A6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px !important;
    }

    /* Premium Glass Cards */
    .apple-card {
        background: rgba(28, 28, 30, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .apple-card:hover {
        transform: translateY(-4px);
        background: rgba(44, 44, 46, 0.8);
        border: 1px solid rgba(10, 132, 255, 0.5);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .inst-text { 
        font-weight: 600; 
        color: #FFFFFF; 
        font-size: 1.15rem; 
        letter-spacing: -0.01em;
    }
    
    .prog-text { 
        color: #A1A1A6; 
        font-size: 0.92rem; 
        margin-top: 6px; 
        line-height: 1.5;
    }
    
    /* Elegant Rank Badge */
    .rank-container {
        display: flex;
        justify-content: flex-start;
        margin-top: 16px;
    }

    .rank-text { 
        color: #0A84FF; 
        font-weight: 700; 
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: rgba(10, 132, 255, 0.15); 
        padding: 6px 12px; 
        border-radius: 20px;
        border: 1px solid rgba(10, 132, 255, 0.2);
    }

    /* Enhanced Inputs */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 12px !important;
        background-color: #1C1C1E !important;
        border: 1px solid #38383A !important;
    }
    
    input { color: #FFFFFF !important; }
    
    .stDivider { border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("DASA Predictor")

@st.cache_data
def load_and_clean_data():
    try:
        df = pd.read_csv("dasa_data.csv")
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'], errors='coerce')
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
        category = st.selectbox("Select Quota", ["DASA-CIWG", "DASA-Non CIWG"])

    st.divider()

    # --- CROSSCHECK LOGIC (Unchanged) ---
    matches = df[
        (df['Quota'] == category) & 
        (rank_input <= df['Closing Rank'])
    ]
    matches = matches.sort_values(by='Closing Rank')

    # --- DISPLAY ---
    if matches.empty:
        st.warning(f"No matches found for Rank {rank_input} in {category}.")
    else:
        st.subheader(f"{len(matches)} Possible Institutes")
        for _, row in matches.iterrows():
            st.markdown(f"""
                <div class="apple-card">
                    <div class="inst-text">{row['Institute']}</div>
                    <div class="prog-text">{row['Academic Program Name']}</div>
                    <div class="rank-container">
                        <span class="rank-text">2025 Closing: {int(row['Closing Rank']):,}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
