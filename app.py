import streamlit as st
import numpy as np

# PROFESSIONAL DATABASE: Real 2024 Closing Ranks (CRL)
COLLEGE_DATA = {
    "Non-CIWG": [
        {"inst": "NIT Surathkal", "branch": "Artificial Intelligence", "rank": 26688},
        {"inst": "NIT Surathkal", "branch": "Computer Science", "rank": 40284},
        {"inst": "NIT Calicut", "branch": "Computer Science", "rank": 112472},
        {"inst": "MNIT Jaipur", "branch": "Computer Science", "rank": 185238},
        {"inst": "NIT Delhi", "branch": "Computer Science", "rank": 509979},
        {"inst": "NIT Durgapur", "branch": "Computer Science", "rank": 556130},
        {"inst": "NIT Goa", "branch": "Computer Science", "rank": 601354},
        {"inst": "NIT Jalandhar", "branch": "Computer Science", "rank": 790430},
        {"inst": "MANIT Bhopal", "branch": "Computer Science", "rank": 1158145},
    ],
    "CIWG": [
        {"inst": "NIT Surathkal", "branch": "Artificial Intelligence", "rank": 31557},
        {"inst": "NIT Calicut", "branch": "Computer Science", "rank": 48693},
        {"inst": "MNIT Jaipur", "branch": "Computer Science", "rank": 108451},
        {"inst": "MNNIT Allahabad", "branch": "Computer Science", "rank": 174196},
        {"inst": "NIT Delhi", "branch": "Computer Science", "rank": 186944},
        {"inst": "NIT Jalandhar", "branch": "Computer Science", "rank": 487117},
        {"inst": "NIT Goa", "branch": "Electrical Engineering", "rank": 1271854},
    ]
}

# FULL SCALE MARKS VS PERCENTILE TABLE (Your provided data)
TREND_DATA = [
    (300, 100.0), (290, 99.999), (280, 99.995), (270, 99.985), (260, 99.98), 
    (250, 99.97), (240, 99.95), (230, 99.93), (220, 99.9), (210, 99.85),
    (200, 99.8), (190, 99.7), (180, 99.6), (170, 99.4), (160, 99.2),
    (150, 99.0), (140, 98.5), (130, 97.8), (120, 97.0), (110, 96.0),
    (100, 93.5), (90, 93.0), (80, 91.0), (70, 88.0), (60, 82.0),
    (50, 75.0), (40, 65.0), (30, 50.0), (20, 40.0), (10, 25.0),
    (0, 17.0), (-20, 0.0)
]

def calculate_percentile(user_marks):
    marks_list = [x[0] for x in TREND_DATA]
    perc_list = [x[1] for x in TREND_DATA]
    # np.interp handles the math for exact numbers in between categories
    return np.interp(user_marks, sorted(marks_list), sorted(perc_list))

def estimate_crl(percentile):
    total_students = 1600000 # Standard 2026 expectation
    rank = (100 - percentile) * total_students / 100
    return int(max(1, rank))

# WEBSITE FRONTEND
st.set_page_config(page_title="DASA 2026 Ultimate Predictor", layout="wide")
st.title("🎓 DASA 2026: Professional Admission Predictor")
st.write("---")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("1. Input Score")
    user_marks = st.number_input("Enter your Marks (-20 to 300):", -20, 300, value=150)
    category = st.radio("DASA Category:", ["Non-CIWG", "CIWG"])
    
    # Run Predictions
    predicted_perc = calculate_percentile(user_marks)
    predicted_rank = estimate_crl(predicted_perc)

    st.success(f"**Predicted Percentile:** {predicted_perc:.4f}%")
    st.info(f"**Estimated JEE CRL Rank:** {predicted_rank:,}")

with col2:
    st.header("2. College Matches")
    st.write(f"Showing results for **{category}** based on 2024 Final Round data:")
    
    eligible = []
    for college in COLLEGE_DATA[category]:
        if predicted_rank <= college["rank"]:
            eligible.append((college, "✅ High Chance"))
        elif predicted_rank <= college["rank"] * 1.2:
            eligible.append((college, "⚠️ Borderline / Moderate"))
            
    if eligible:
        for c, status in eligible:
            with st.expander(f"{status}: {c['inst']} - {c['branch']}"):
                st.write(f"**Last Year Closing Rank:** {c['rank']:,}")
                st.write(f"**Your Predicted Rank:** {predicted_rank:,}")
    else:
        st.warning("No matches found in top NITs. Consider newer IIITs or non-CSE branches.")

st.write("---")
st.caption("Note: This tool uses 2022-2024 trends to forecast 2026 possibilities. Actual cutoffs vary year-on-year.")
