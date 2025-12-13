import streamlit as st

def risk_category():
    st.header("4️⃣ Risk Category")
    risk_map = {
        "I": "Low risk to human life (e.g., storage, barns)",
        "II": "Typical occupancy (residential, commercial, offices)",
        "III": "Substantial hazard to human life (schools, assemblies)",
        "IV": "Essential facilities (hospitals, emergency services)"
    }
    category = st.selectbox("Select Risk Category", list(risk_map.keys()),
                            format_func=lambda x: f"Category {x} – {risk_map[x].split('(')[0]}")
    st.info(risk_map[category])
    st.markdown("---")
    return category
