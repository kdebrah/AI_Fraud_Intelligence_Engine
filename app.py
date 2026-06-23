import streamlit as st
from search_engine import search_similar_cases

st.title("AI Fraud Intelligence Engine")

st.write("Semantic Search for Fraud Cases")

query = st.text_input(
    "Enter fraud scenario:",
    placeholder= "e.g rapid deposits through customer accounts"
)

if st.button("Search"):
    results = search_similar_cases(
        query,
        min_score=0.50
    )

    for r in results:
        
        st.subheader(f"Case ID: {r['case_id']}")

        st.write(f"**Fraud Type:** {r['type']}")
        st.write(f"**Country:** {r['country']}")
        st.write(f"**Similarity Score:** {round(r['score'],3)}")
        st.write(f"**Risk Level:** {r['risk_level']}")

        st.write("### Description")
        st.write(r["description"])

        st.write("### AI Explanation")
        st.write(r["explanation"])

        st.divider()