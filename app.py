import streamlit as st
import pandas as pd
import numpy as np

# --- 1. PREMIUM UI SETUP ---
st.set_page_config(page_title="DASA 2026 Master Predictor", layout="wide")

# Custom CSS for a clean, professional "SaaS" look
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .main-header { color: #f1c40f; font-size: 2.5rem; font-weight: 800; margin-bottom: 20px; }
    .card { 
        background-color: #1c212d; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 6px solid #f1c40f;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .card:hover { transform: scale(1.01); background-color: #252b38; }
    .stat-box { background: #262730; padding: 15px; border-radius: 10px; border: 1px solid #3e4149; }
    .tag-safe { color: #2ecc71; font-weight: bold; background: rgba(46, 204, 113, 0.1); padding: 4px 8px; border-radius: 5px; }
    .tag-border { color: #f1c40f; font-weight: bold; background: rgba(241, 196, 15, 0.1); padding: 4px 8px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADING ---
@st.cache_data
def load_college_data():
    try:
        df = pd.read_csv("dasa_data.csv")
        # CLEANUP: Remove hidden spaces from column names
        df.columns = df.columns.str.strip() 
        
        # DEBUG: If the app fails, this will show you the real column names
        expected = ['Category', 'Institute', 'Branch', 'Closing Rank']
        for col in expected:
            if col not in df.columns:
                st.error(f"❌ Column '{col}' not found! Your CSV has: {list(df.columns)}")
                st.stop()
        return df
    except Exception as e:
        st.error(f"Could not read CSV file: {e}")
        return None

# --- 3. THE "BETTER" FEATURES ---
st.markdown('<h1 class="main-header">🎓 DASA 2026 Rank Predictor</h1>', unsafe_allow_html=True)

if df is not None:
    # SIDEBAR CONTROLS
    st.sidebar.header("🎯 Target & Filters")
    user_rank = st.sidebar.number_input("Enter Your JEE CRL Rank", value=50000, step=1000)
    category = st.sidebar.selectbox("DASA Category", ["Non-CIWG", "CIWG"])
    
    # Feature 1: Safety Buffer (Predicting 2026 hardness)
    buffer = st.sidebar.slider("Volatility Buffer (%)", 0, 20, 5)
    effective_rank = user_rank * (1 + buffer/100)
    
    st.sidebar.divider()
    institute_type = st.sidebar.multiselect("Institute Type", options=df['Type'].unique() if 'Type' in df.columns else ["NIT", "IIIT", "CF TI", "Other"])
    
    # MAIN LAYOUT
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📊 Analysis")
        st.markdown(f"""
        <div class="stat-box">
            <small>ADJUSTED RANK FOR 2026</small><br>
            <strong style="font-size: 24px; color: #f1c40f;">{int(effective_rank):,}</strong><br>
            <p style="font-size: 0.8em; color: #888; margin-top:10px;">
            We added a {buffer}% buffer to account for 2026 competition increases.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 **Pro Tip:** Ranks in DASA can jump significantly. Always look for colleges where your rank is at least 10% better than last year's closing.")

    with col2:
        st.markdown(f"### 🏛️ College Matches for {category}")
        
        # Filter Logic
        # Note: Ensure these column names match your CSV exactly (e.g., 'Category', 'Closing Rank')
        mask = (df['Category'] == category)
        filtered = df[mask].copy()
        
        # Search functionality
        search_query = st.text_input("🔍 Search by College or City", "")
        if search_query:
            filtered = filtered[filtered['Institute'].str.contains(search_query, case=False) | 
                                filtered['Branch'].str.contains(search_query, case=False)]

        # Sorting: Show closest matches first
        filtered = filtered.sort_values(by='Closing Rank')

        # Display Loop
        match_count = 0
        for _, row in filtered.iterrows():
            cutoff = row['Closing Rank']
            
            # Logic for color coding
            if user_rank <= cutoff:
                status_html = '<span class="tag-safe">HIGH PROBABILITY</span>'
                card_border = "#2ecc71"
            elif user_rank <= cutoff * 1.2:
                status_html = '<span class="tag-border">MODERATE / RISKY</span>'
                card_border = "#f1c40f"
            else:
                continue # Hide colleges that are way out of reach

            st.markdown(f"""
            <div class="card" style="border-left-color: {card_border};">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4 style="margin:0;">{row['Institute']}</h4>
                        <p style="margin:0; color: #bbb; font-size: 0.9em;">{row['Branch']}</p>
                    </div>
                    <div style="text-align: right;">
                        {status_html}<br>
                        <small style="color: #888;">'25 Cutoff: {int(cutoff):,}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            match_count += 1

        if match_count == 0:
            st.warning("No matches found for this rank. Try adjusting your filters or buffer.")

else:
    st.error("Please ensure 'dasa_data.csv' is uploaded to the repository.")
