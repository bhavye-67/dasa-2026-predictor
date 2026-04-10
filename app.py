import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="DASA 2026 Master Predictor", layout="wide")

@st.cache_data
def load_college_data():
    try:
        df = pd.read_csv("dasa_data.csv")
        df.columns = df.columns.str.strip() 
        
        # Exact matching for your headers
        rename_dict = {
            'Institute': 'Institute',
            'Academic Program Name': 'Branch',
            'Quota': 'Category',
            'Closing Rank': 'Closing Rank'
        }
        
        # Check if they exist
        for old, new in rename_dict.items():
            if old not in df.columns:
                return None, f"Missing column: {old}"
        
        df = df.rename(columns=rename_dict)
        # Fix Rank format (remove commas and convert to number)
        df['Closing Rank'] = pd.to_numeric(df['Closing Rank'].astype(str).str.replace(',', ''), errors='coerce')
        return df.dropna(subset=['Closing Rank']), None
    except Exception as e:
        return None, str(e)

df, err = load_college_data()

st.title("🏛️ DASA 2026 Master Predictor")

if df is not None:
    # --- DEBUG SECTION (You can delete this after it works) ---
    with st.expander("🛠️ Debug: See your file data"):
        st.write("Unique Categories in your file:", df['Category'].unique().tolist())
        st.write("First 5 rows of data:", df.head())
    # ---------------------------------------------------------

    st.sidebar.header("🎯 Target Rank")
    user_rank = st.sidebar.number_input("JEE Main CRL Rank", value=50000)
    
    # Check if we should use CIWG or something else
    available_cats = df['Category'].unique().tolist()
    category = st.sidebar.selectbox("Category", available_cats)
    
    search = st.sidebar.text_input("🔍 Search College")
    buffer = st.sidebar.slider("2026 Buffer (%)", 0, 20, 5)
    effective_rank = user_rank * (1 + buffer/100)

    results = df[df['Category'] == category].copy()
    
    if search:
        results = results[results['Institute'].str.contains(search, case=False) | 
                         results['Branch'].str.contains(search, case=False)]

    results = results.sort_values(by='Closing Rank')
    
    # Filter: Show colleges where cutoff is better than user's rank
    final_list = results[results['Closing Rank'] >= effective_rank * 0.7]

    if final_list.empty:
        st.warning(f"No colleges found for Rank {int(effective_rank)} in category '{category}'.")
    else:
        for _, row in final_list.iterrows():
            is_safe = effective_rank <= row['Closing Rank']
            color = "#2ecc71" if is_safe else "#f1c40f"
            tag = "✅ SAFE" if is_safe else "⚠️ BORDERLINE"
            
            st.markdown(f"""
                <div style="background:#1c212d; padding:15px; border-radius:10px; border-left:5px solid {color}; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <h4 style="margin:0;">{row['Institute']}</h4>
                        <span style="color:{color}; font-weight:bold;">{tag}</span>
                    </div>
                    <p style="margin:5px 0; color:#bbb;">{row['Branch']}</p>
                    <p style="margin:0; color:#f1c40f; font-size:0.9em;">2025 Cutoff: {int(row['Closing Rank']):,}</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.error(f"Failed to load data: {err}")
