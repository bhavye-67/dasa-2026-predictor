import streamlit as st
import pandas as pd

# --- ENHANCED APPLE PRO UI ---
st.set_page_config(page_title="DASA 2026 Predictor", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #000000;
        color: #F5F5F7;
    }
    
    /* Midnight Gradient Background */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1c1c1e 0%, #000000 80%);
    }

    /* Title Styling */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        background: linear-gradient(180deg, #FFFFFF 0%, #A1A1A6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding-bottom: 20px;
    }

    /* Premium Glass Card Design */
    .apple-card {
        background: rgba(28, 28, 30, 0.7);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    }
    
    .apple-card:hover {
        transform: scale(1.02);
        background: rgba(44, 44, 46, 0.9);
        border: 1px solid rgba(10, 132, 255, 0.6);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
    }
    
    .inst-text { 
        font-weight: 600; 
        color: #FFFFFF; 
        font-size: 1.2rem; 
        letter-spacing: -0.01em;
    }
    
    .prog-text { 
        color: #A1A1A6; 
        font-size: 0.95rem; 
        margin-top: 8px; 
        line-height: 1.6;
    }
    
    /* iOS Blue Badge */
    .rank-badge-container {
        display: flex;
        margin-top: 18px;
    }

    .rank-badge { 
        color: #0A84FF; 
        font-weight: 700; 
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        background: rgba(10, 132, 255, 0.12); 
        padding: 8px 14px; 
        border-radius: 100px;
        border: 1px solid rgba(10, 132, 255, 0.3);
    }

    /* Modern Styled Inputs */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 14px !important;
        background-color: #1C1C1E !important;
        border: 1px solid #3A3A3C !important;
    }
    
    input { color: #FFFFFF !important; font-weight: 500 !important; }
    
    label { color: #A1A1A6 !important; font-weight: 500 !important; margin-bottom: 8px !important; }

    .stDivider { border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("DASA Predictor")

# --- DATA ENGINE ---
@st.cache_data
def load_and_clean_data():
    try:
        # Strictly using the file from your GitHub
        df = pd.read_csv("dasa_data.csv")
        # Ensure ranks are processed as clean numbers
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'], errors='coerce')
        # Drop rows that don't have a valid rank
        return df.dropna(subset=['Closing Rank'])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_and_clean_data()

if df is not None:
    # --- INPUT SECTION ---
    col1, col2 = st.columns(2)
    with col1:
        rank_input = st.number_input("Enter Your JEE Rank", min_value=1, value=50000)
    with col2:
        # Limited strictly to your requested DASA options
        category = st.selectbox("Select Your Quota", ["DASA-CIWG", "DASA-Non CIWG"])

    st.divider()

    # --- CROSSCHECK LOGIC ---
    # Filter by user's quota and check if user rank is within the closing rank
    matches = df[
        (df['Quota'] == category) & 
        (rank_input <= df['Closing Rank'])
    ]
    
    # Sort by rank so the most competitive institutes appear first
    matches = matches.sort_values(by='Closing Rank')

    # --- DISPLAY MATCHES ---
    if matches.empty:
        st.warning(f"No matches found for Rank {rank_input:,} in the {category} category.")
    else:
        st.subheader(f"{len(matches)} Matching Institutes Found")
        for _, row in matches.iterrows():
            st.markdown(f"""
                <div class="apple-card">
                    <div class="inst-text">{row['Institute']}</div>
                    <div class="prog-text">{row['Academic Program Name']}</div>
                    <div class="rank-badge-container">
                        <span class="rank-badge">2025 Closing: {int(row['Closing Rank']):,}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("Ensure 'dasa_data.csv' is uploaded to your GitHub repository.")
