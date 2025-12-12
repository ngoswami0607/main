import streamlit as st


def roof_type_picker(height_ft: float) -> dict:
    h = float(height_ft)

    st.header("2️⃣ Roof Type")  # since you're inserting after Step 1

    roof_low_rise = [
        "Flat roof",
        "Gable roof",
        "Hip roof",
        "Monoslope roof",
        "Stepped roof",
        "Multiple gable roof",
        "Sawtooth roof",
        "Domed roof",
        "Arched roof",
    ]

    roof_high = roof_low_rise + ["Other / Not listed"]

    if h <= 60.0:
        st.info("h ≤ 60 ft → Low-rise C&C path (ASCE 7-16 Chapter 30.3).")
        roof = st.selectbox("Roof type:", roof_low_rise, key="roof_type_lowrise")
        ref = "Use Chapter 30.3 roof figures for (GCp) for the selected roof type."
        result = {"height_band": "<=60", "roof_type": roof, "ref": ref}

    elif 60.0 < h <= 160.0:
        st.info("60 ft < h ≤ 160 ft → Use Chapter 30.6 procedure (as applicable) + correct (GCp) figures.")
        roof = st.selectbox("Roof type:", roof_high, key="roof_type_30_6")
        ref = "Use Chapter 30.6 procedure + appropriate Chapter 30 figures for (GCp)."
        result = {"height_band": "60-160", "roof_type": roof, "ref": ref}

    else:
        st.info("h > 160 ft → Use Table 30.5-1 workflow + correct (GCp) figures.")
        roof = st.selectbox("Roof type:", roof_high, key="roof_type_30_5_1")
        ref = "Use Table 30.5-1 workflow + appropriate Chapter 30 figures for (GCp)."
        result = {"height_band": ">160", "roof_type": roof, "ref": ref}

    st.caption(result["ref"])
    st.markdown("---")

    # Optional: persist for other steps
    st.session_state["roof_info"] = result
    return result
