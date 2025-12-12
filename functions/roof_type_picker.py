def roof_type_picker(height_ft: float) -> dict:
    h = float(height_ft)

    st.subheader("Roof Type")

    roof_low_rise = {"Flat roof","Gable roof", "Hip roof", "Monoslope roof", "Stepped roof", "Multiple gable roof",  "Sawtooth roof",  "Domed roof", "Arched roof"}

    roof_high = {"Flat roof", "Gable roof", "Hip roof", "Monoslope roof", "Stepped roof", "Multiple gable roof", "Sawtooth roof", "Domed roof", "Arched roof", "Other / Not listed"}

    if h <= 60.0:
        st.info("h ≤ 60 ft → Low-rise Components & Cladding path (ASCE 7-16 Chapter 30.3).")
        roof = st.selectbox("Roof type:", list(roof_low_rise.keys()), key="roof_type_lowrise")
        return {"height_band": "<=60", "roof_type": roof, "ref": roof_low_rise[roof]}

    if 60.0 < h <= 160.0:
        st.info("60 ft < h ≤ 160 ft → Use Chapter 30.6 procedure (as applicable) + correct GCp figures.")
        roof = st.selectbox("Roof type:", list(roof_high.keys()), key="roof_type_30_6")
        return {"height_band": "60-160", "roof_type": roof, "ref": f"Ch.30.6 band: {roof_high[roof]}"}

    st.info("h > 160 ft → Use Table 30.5-1 workflow + correct GCp figures.")
    roof = st.selectbox("Roof type:", list(roof_high.keys()), key="roof_type_30_5_1")
    return {"height_band": ">160", "roof_type": roof, "ref": f"Table 30.5-1 workflow: {roof_high[roof]}"}
