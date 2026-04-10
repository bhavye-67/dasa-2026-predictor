import streamlit as st
import pandas as pd
import numpy as np

# 1. PAGE SETUP
st.set_page_config(page_title="DASA 2026 Master Predictor", layout="wide")

# 2. FAIL-SAFE DATA LOADER
@st.cache_data
def load_college_data():
    try:
        # Load the CSV
        df = pd.read_csv("dasa_data.csv")
        # Clean headers (removes hidden spaces/newlines)
        df.columns = df.columns.str.strip() 
        
        # Mapping your exact headers to simplified names for the code
        # Your headers: Institute, Academic Program Name, Quota, Opening Rank, Closing Rank
        rename_dict = {
            'Institute': 'Institute',
            'Academic Program Name': 'Branch',
            'Quota': 'Category',
            'Opening Rank': 'OR',
            'Closing Rank': 'Closing Rank'
        }
        
        # Ensure the columns actually exist before renaming
        for original in rename_dict.keys():
            if original not in df.columns:
                return None, f"❌ Header mismatch! Missing: '{original}'. Found: {list(df.columns)}"
        
        df = df.rename(columns=rename_dict)
        
        # CLEAN DATA: Convert Closing Rank to numeric (removes commas if any)
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'].astype(str).str.replace(',', ''), errors='coerce')
        df = df.dropna(subset=['Closing Rank']) # Remove rows with broken rank data
        
        return df, None
    except Exception as e:
        return None, str(e)

df, error_msg = load_college_data()

# 3. PREMIUM DARK UI
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

# 4. APP LOGIC
st.title("🏛️ DASA 2026 Master Predictor")

if df is not None:
    st.sidebar.header("🎯 Target Rank")
    user_rank = st.sidebar.number_input("Enter JEE Main CRL Rank", min_value=1, value=50000)
    
    # Matching the Quota names from your file
    category = st.sidebar.selectbox("Category", ["Non-CIWG", "CIWG"])
    
    # SEARCH FEATURE (Makes it better than DASA Compass)
    search = st.sidebar.text_input("🔍 Search College or Branch")
    
    st.sidebar.divider()
    buffer = st.sidebar.slider("2026 Volatility Buffer (%)", 0, 20, 5)
    effective_rank = user_rank * (1 + buffer/100)

    # OUTPUT
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.subheader("Your Analysis")
        st.metric("Effective Rank", f"{int(effective_rank):,}")
        st.caption(f"Accounting for a {buffer}% competition spike in 2026.")
        st.divider()
        st.info("💡 Pro Tip: Borderline colleges are great choices for 'Internal Sliding'.")

    with col2:
        st.subheader(f"Matches for {category}")
        
        # Filter by Category and Search
        results = df[df['Category'] == category].copy()
        if search:
            results = results[results['Institute'].str.contains(search, case=False) | 
                             results['Branch'].str.contains(search, case=False)]
        
        # Sort so best colleges (lower closing rank) show first
        results = results.sort_values(by='Closing Rank')
        
        found = False
        for _, row in results.iterrows():
            cutoff = row['Closing Rank']
            
            # Show if user rank is within reasonable distance (30% buffer)
            if effective_rank <= cutoff * 1.3:
                found = True
                is_safe = effective_rank <= cutoff
                tag = '<span class="safe-tag">✅ SAFE</span>' if is_safe else '<span class="risky-tag">⚠️ BORDERLINE</span>'
                
                st.markdown(f"""
                    <div class="college-card">
                        <div style="display: flex; justify-content: space-between;">
                            <h4 style="margin:0;">{row['Institute']}</h4>
                            {tag}
                        </div>
                        <p style="margin:5px 0; color: #bbb;">{row['Branch']}</p>
                        <p style="margin:0; font-size: 0.85em; color: #f1c40f;">2025 Closing Rank: {int(cutoff):,}</p>
                    </div>
                """, unsafe_allow_html=True)

        if not found:
            st.warning("No matches found. Try a different rank or check your search terms.")

else:
    st.error("🚨 Data Loading Failed")
    st.write(f"Details: {error_msg}")
    st.info("Check your 'dasa_data.csv' headers. They must be: Institute, Academic Program Name, Quota, Opening Rank, Closing Rank")
