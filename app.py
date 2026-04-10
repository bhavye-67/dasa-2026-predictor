import streamlit as st
import pandas as pd
import numpy as np

# 1. PAGE SETUP
st.set_page_config(page_title="DASA 2026 Rank Predictor", layout="wide")

# 2. SMART DATA LOADER
@st.cache_data
def load_college_data():
    try:
        # Load the CSV
        df = pd.read_csv("dasa_data.csv")
        df.columns = df.columns.str.strip() # Remove spaces from headers
        
        # This mapping makes the app work even if your CSV column names change slightly
        col_map = {}
        for col in df.columns:
            c_low = col.lower()
            if 'inst' in c_low: col_map[col] = 'Institute'
            elif 'Academic Program Name' in c_low or 'prog' in c_low: col_map[col] = 'Academic Program Name'
            elif 'rank' in c_low or 'close' in c_low: col_map[col] = 'Closing Rank'
            elif 'cat' in c_low or 'quota' in c_low: col_map[col] = 'Category'
        
        df = df.rename(columns=col_map)
        
        # Final check for essential columns
        required = ['Institute', 'Academic Program Name', 'Closing Rank', 'Category']
        for req in required:
            if req not in df.columns:
                return None, f"Missing column: {req}. Found: {list(df.columns)}"
        
        # Ensure ranks are numbers
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'], errors='coerce')
        return df, None
    except Exception as e:
        return None, str(e)

# Initialize data
df, error_msg = load_college_data()

# 3. UI STYLE
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .college-card { 
        background-color: #1c212d; padding: 20px; border-radius: 12px; 
        border-left: 6px solid #f1c40f; margin-bottom: 15px;
    }
    .safe-tag { color: #2ecc71; font-weight: bold; font-size: 0.8em; border: 1px solid #2ecc71; padding: 2px 8px; border-radius: 5px; }
    .risky-tag { color: #f1c40f; font-weight: bold; font-size: 0.8em; border: 1px solid #f1c40f; padding: 2px 8px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 4. MAIN APP LOGIC
st.title("🏛️ DASA 2026 Master Predictor")

if df is not None:
    # Sidebar for Inputs
    st.sidebar.header("🎯 Input Your Stats")
    user_rank = st.sidebar.number_input("JEE Main CRL Rank", min_value=1, value=50000, step=1000)
    category = st.sidebar.selectbox("Category", ["Non-CIWG", "CIWG"])
    
    # "Better" Feature: Safety Buffer
    # This accounts for the 2026 competition increase
    st.sidebar.divider()
    buffer = st.sidebar.slider("Volatility Buffer (%)", 0, 20, 5)
    effective_rank = user_rank * (1 + buffer/100)
    
    # Layout
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.subheader("Your Profile")
        st.metric("Effective Rank", f"{int(effective_rank):,}", delta=f"+{buffer}% Buffer", delta_color="inverse")
        st.write(f"Category: **{category}**")
        st.info("The Safety Buffer treats your rank as 'lower' to protect you against 2026 competition spikes.")

    with col2:
        st.subheader("Predicted College Matches")
        
        # Filtering
        results = df[df['Category'] == category].copy()
        
        # Sort by Closing Rank (most prestigious first)
        results = results.sort_values(by='Closing Rank')
        
        found = False
        for _, row in results.iterrows():
            cutoff = row['Closing Rank']
            
            # Skip if way out of range (user rank > 1.3x the cutoff)
            if effective_rank > cutoff * 1.3:
                continue
            
            found = True
            is_safe = effective_rank <= cutoff
            status_tag = '<span class="safe-tag">✅ SAFE</span>' if is_safe else '<span class="risky-tag">⚠️ BORDERLINE</span>'
            
            st.markdown(f"""
                <div class="college-card">
                    <div style="display: flex; justify-content: space-between;">
                        <h4 style="margin:0;">{row['Institute']}</h4>
                        {status_tag}
                    </div>
                    <p style="margin:5px 0; color: #bbb;">{row['Academic Program Name']}</p>
                    <p style="margin:0; font-size: 0.85em; color: #f1c40f;">2025 Closing Rank: {int(cutoff):,}</p>
                </div>
            """, unsafe_allow_html=True)
            
        if not found:
            st.warning("No matches found for this rank. Try lowering the buffer or checking different categories.")

else:
    # This handles the case where the file is missing or formatted wrong
    st.error("🚨 Data Loading Failed")
    st.write(f"Details: {error_msg}")
    st.info("Check your 'dasa_data.csv' file and make sure the columns are named correctly.")
