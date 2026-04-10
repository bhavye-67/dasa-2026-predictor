import streamlit as st
import pandas as pd

# --- APPLE DARK UI SETUP ---
st.set_page_config(page_title="DASA Predictor", layout="centered")

st.markdown("""
    <style>
    /* Apple-like typography and dark mode colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #000000;
        color: #F5F5F7;
    }
    
    .stApp { background-color: #000000; }
    
    /* Clean, translucent card style */
    .apple-card {
        background-color: #1C1C1E;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid #38383A;
    }
    
    .apple-title { 
        font-size: 1.15rem; 
        font-weight: 600; 
        color: #FFFFFF; 
        margin-bottom: 4px; 
    }
    
    .apple-subtitle { 
        font-size: 0.95rem; 
        color: #86868B; 
        margin-bottom: 12px; 
    }
    
    .apple-rank { 
        display: inline-block;
        background-color: #2C2C2E;
        color: #2997FF; /* iOS Blue */
        padding: 5px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Input field styling */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1C1C1E !important;
        color: white !important;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("DASA Predictor")

# --- DATA LOADER ---
@st.cache_data
def load_data():
    # Reads strictly from your GitHub file
    df = pd.read_csv("dasa_data.csv")
    df.columns = df.columns.str.strip()
    
    # Ensures 'Closing Rank' is read as a clean number
    if 'Closing Rank' in df.columns:
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'].astype(str).str.replace(',', ''), errors='coerce')
    
    return df.dropna(subset=['Closing Rank'])

try:
    df = load_data()
    
    # --- USER INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        user_rank = st.number_input("Enter Your Rank", min_value=1, value=50000, step=1000)
    with col2:
        # Dynamically pulls Quotas (CIWG, Non-CIWG, etc.) from your file
        available_quotas = df['Quota'].unique()
        user_quota = st.selectbox("Select Quota", available_quotas)
        
    st.divider()
    
    # --- RAW DATA FILTERING ---
    # Cross-checks your rank against the file (shows colleges where cutoff is >= your rank)
    matches = df[(df['Quota'] == user_quota) & (df['Closing Rank'] >= user_rank)]
    
    # Sorts so the hardest colleges to get into show up first
    matches = matches.sort_values(by='Closing Rank')
    
    # --- OUTPUT ---
    if matches.empty:
        st.warning("No matching institutes found for this rank in the dataset.")
    else:
        for _, row in matches.iterrows():
            st.markdown(f"""
            <div class="apple-card">
                <div class="apple-title">{row['Institute']}</div>
                <div class="apple-subtitle">{row['Academic Program Name']}</div>
                <div class="apple-rank">Last Year's Rank: {int(row['Closing Rank']):,}</div>
            </div>
            """, unsafe_allow_html=True)
            
except FileNotFoundError:
    st.error("⚠️ 'dasa_data.csv' not found. Please make sure the file is uploaded to your GitHub repo exactly with this name.")
except Exception as e:
    st.error(f"⚠️ Error: Make sure your file has the exact headers: Institute, Academic Program Name, Quota, Closing Rank. Detailed error: {e}")
