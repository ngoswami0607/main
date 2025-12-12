import streamlit as st

def wind_pressure_calc(height, V):
    # this should change based on code jurisditcion
    st.header("5️⃣ Basic Wind Pressure Calculation (ASCE 7-16)")

    # --- Directionality Factor (Kd) ---
    structure_types = {
        #"Buildings – MWFRS": 0.85,
        "Buildings – Components & Cladding": 0.85,
        "Arched Roofs": 0.85,
        "Circular Domes (Axisymmetric)": 1.00,
        "Circular Domes (Non-axisymmetric system)": 0.95,
        "Chimneys / Tanks – Square": 0.90,
        "Chimneys / Tanks – Hexagonal": 0.95,
        "Chimneys / Tanks – Octagonal": 1.00,
        "Chimneys / Tanks – Round": 1.00,
        "Chimneys / Tanks – Octagonal (Non-axisymmetric system)": 0.95,
        "Chimneys / Tanks – Round (Non-axisymmetric system)": 0.95,
        "Solid Freestanding Walls": 0.85,
        "Rooftop Equipment (Solid)": 0.85,
        "Attached Signs (Solid)": 0.85,
        "Open Signs": 0.85,
        "Single-Plane Open Frames": 0.85,
        "Trussed Towers – Triangular / Square / Rectangular": 0.85,
        "Trussed Towers – All Other Cross-Sections": 0.95,
    }

    structure = st.selectbox("Structure Type:", list(structure_types.keys()))
    Kd = structure_types[structure]

    def exposure_category_picker_cards() -> str:
        st.subheader("Exposure Category")

    exposure_meta = {
        "B": {
            "label": "Urban/suburban/wooded; roughness B upwind ≥1500 ft (h≤30) or ≥2600 ft/20h (h>30).",
            "img": "photos_Exposure_Cat/exposure_B.png",
        },
        "C": {
            "label": "Open terrain w/ scattered obstructions; default when B or D does not apply.",
            "img": "photos_Exposure_Cat/exposure_C.png",
        },
        "D": {
            "label": "Flat unobstructed/water; roughness D upwind ≥5000 ft/20h, or within 600 ft/20h of D.",
            "img": "photos_Exposure_Cat/exposure_D.png",
        },
    }

    # Keep state
    if "exposure_category" not in st.session_state:
        st.session_state["exposure_category"] = "C"

    cols = st.columns(3)
    for col, key in zip(cols, ["B", "C", "D"]):
        with col:
            st.image(exposure_meta[key]["img"], use_container_width=True)
            st.write(f"**Exposure {key}**")
            st.caption(exposure_meta[key]["label"])
            if st.button(f"Choose {key}", key=f"choose_exposure_{key}"):
                st.session_state["exposure_category"] = key

    chosen = st.session_state["exposure_category"]
    st.success(f"Selected Exposure {chosen}")
    st.markdown("---")
    return chosen

    
    exposure = st.selectbox("Exposure Category:", ["B", "C", "D"], index=1)

    def get_kz(h, exposure):
        table = {"B": 0.70, "C": 0.98, "D": 1.16}
        return table.get(exposure, 1.0)

    Kz = get_kz(height, exposure)
    Kzt, Ke = 1.0, 1.0
    q = 0.00256 * Kz * Kzt * Kd * Ke * (V ** 2)

    st.metric(label="Velocity Pressure (q)", value=f"{q:.2f} psf")
    st.markdown("---")
