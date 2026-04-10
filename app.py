import streamlit as st
import pandas as pd

# --- APPLE DARK THEME UI ---
st.set_page_config(page_title="DASA 2026", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #000000;
        color: #FFFFFF;
    }
    
    .stApp { background-color: #000000; }

    /* Modern Apple-like Cards */
    .college-card {
        background: rgba(28, 28, 30, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease;
    }
    
    .college-card:hover {
        transform: translateY(-2px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .inst-name { color: #FFFFFF; font-weight: 600; font-size: 1.1rem; margin-bottom: 4px; }
    .prog-name { color: #8E8E93; font-size: 0.9rem; margin-bottom: 12px; }
    .rank-tag { 
        display: inline-block;
        background: rgba(255, 255, 255, 0.1); 
        padding: 4px 10px; 
        border-radius: 8px; 
        font-size: 0.85rem; 
        color: #0A84FF;
        font-weight: 600;
    }

    /* Input Styling */
    .stNumberInput, .stSelectbox { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINE ---
@st.cache_data
def get_data():
    try:
        df = pd.read_csv("dasa_data.csv")
        df.columns = df.columns.str.strip()
        # Cleaning Rank data (removing commas/converting to numbers)
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'].astype(str).str.replace(',', ''), errors='coerce')
        return df.dropna(subset=['Closing Rank'])
    except Exception as e:
        st.error(f"Error loading dasa_data.csv: {e}")
        return None

df = get_data()

# --- APP LAYOUT ---
st.title("🏛️ Predictor")
st.write("Using 2025 official data from your GitHub repository.")

if df is not None:
    # Top Section: Inputs
    c1, c2 = st.columns(2)
    with c1:
        user_rank = st.number_input("Enter your JEE CRL Rank", min_value=1, value=50000, step=1000)
    with c2:
        # Pulls Quotas directly from your file (e.g., CIWG, Non-CIWG)
        q_options = df['Quota'].unique().tolist()
        user_quota = st.selectbox("Select your Quota", q_options)

    st.write("---")

    # Filtering Logic
    results = df[df['Quota'] == user_quota].copy()
    
    # Cross-check: We show colleges where your rank is better than (or very close to) the cutoff
    # Sort by rank to show best institutes first
    results = results.sort_values(by='Closing Rank')

    # Filtering for display: only show stuff the user could actually get (with a 20% buffer)
    matches = results[results['Closing Rank'] >= user_rank * 0.8]

    if matches.empty:
        st.warning("No institutes found in the data matching this rank.")
    else:
        # Grid layout for results
        for _, row in matches.iterrows():
            st.markdown(f"""
                <div class="college-card">
                    <div class="inst-name">{row['Institute']}</div>
                    <div class="prog-name">{row['Academic Program Name']}</div>
                    <div class="rank-tag">2025 Rank: {int(row['Closing Rank']):,}</div>
                </div>
            """, unsafe_allow_html=True)

else:
    st.info("Please ensure 'dasa_data.csv' is in your GitHub repo with headers: Institute, Academic Program Name, Quota, Closing Rank.")

st.caption("Admin Mode: Dynamic CSV integration active.")
