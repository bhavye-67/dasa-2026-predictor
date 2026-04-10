import streamlit as st
import pandas as pd

st.set_page_config(page_title="DASA 2026 - Data Verified", layout="wide")

@st.cache_data
def load_strict_data():
    try:
        # 1. Load your specific file
        df = pd.read_csv("dasa_data.csv")
        df.columns = df.columns.str.strip()
        
        # 2. Map your exact column names
        # Institute, Academic Program Name, Quota, Opening Rank, Closing Rank
        rename_map = {
            'Institute': 'Inst',
            'Academic Program Name': 'Program',
            'Quota': 'Quota',
            'Closing Rank': 'Cutoff'
        }
        
        # Verify columns exist
        for col in rename_map.keys():
            if col not in df.columns:
                st.error(f"⚠️ Column '{col}' is missing from your CSV!")
                st.stop()
                
        df = df.rename(columns=rename_map)
        
        # 3. Clean the Ranks (Remove commas/strings)
        df['Cutoff'] = pd.to_numeric(df['Cutoff'].astype(str).str.replace(',', ''), errors='coerce')
        return df.dropna(subset=['Cutoff'])
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = load_strict_data()

# --- THE UI ---
st.title("🎯 Verified DASA 2026 Predictor")
st.write("---")

if df is not None:
    # Sidebar Filters
    st.sidebar.header("User Input")
    my_rank = st.sidebar.number_input("Your JEE CRL Rank", value=50000)
    
    # Dynamically pull Quotas from YOUR data (CIWG/Non-CIWG)
    available_quotas = df['Quota'].unique().tolist()
    my_quota = st.sidebar.selectbox("Select Quota", available_quotas)
    
    # Search Filter
    search_query = st.sidebar.text_input("Search (e.g., 'Trichy' or 'CSE')")

    # --- FILTERING LOGIC ---
    # We only look at your selected Quota
    filtered = df[df['Quota'] == my_quota].copy()
    
    if search_query:
        filtered = filtered[
            filtered['Inst'].str.contains(search_query, case=False) | 
            filtered['Program'].str.contains(search_query, case=False)
        ]

    # --- DISPLAY ---
    st.subheader(f"Results for {my_quota} (Total: {len(filtered)} branches found)")
    
    # Logic: Show colleges where the cutoff is "close" to the user rank
    # We show anything where the user's rank is better than or near the cutoff
    matches = filtered[filtered['Cutoff'] >= my_rank * 0.7].sort_values('Cutoff')

    if matches.empty:
        st.warning("No matches found in your data for this rank.")
    else:
        for _, row in matches.iterrows():
            is_safe = my_rank <= row['Cutoff']
            status = "✅ SAFE" if is_safe else "⚠️ BORDERLINE"
            card_color = "#2ecc71" if is_safe else "#f1c40f"
            
            st.markdown(f"""
                <div style="background:#1c212d; padding:15px; border-radius:10px; border-left:6px solid {card_color}; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:white;">{row['Inst']}</h4>
                        <span style="color:{card_color}; font-weight:bold;">{status}</span>
                    </div>
                    <p style="margin:5px 0; color:#aaa; font-size:0.9em;">{row['Program']}</p>
                    <p style="margin:0; color:#f1c40f; font-weight:bold;">2025 Closing: {int(row['Cutoff']):,}</p>
                </div>
            """, unsafe_allow_html=True)

# --- DEBUG TOOLS ---
with st.expander("🔍 Inspect Data (Check if NIT Meghalaya is really here)"):
    if df is not None:
        st.write("First 10 rows of your file:")
        st.dataframe(df.head(10))
        if st.button("Check for NIT Meghalaya"):
            check = df[df['Inst'].str.contains("Meghalaya", case=False)]
            if check.empty:
                st.write("❌ NIT Meghalaya is NOT in your CSV.")
            else:
                st.write("✅ NIT Meghalaya FOUND in your CSV:")
                st.write(check)
