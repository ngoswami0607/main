import base64
import streamlit as st


def _img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _fixed_image(path: str, height_px: int = 140, border_radius_px: int = 12) -> None:
    b64 = _img_to_base64(path)
    st.markdown(
        f"""
        <div style="width: 100%; height: {height_px}px; overflow: hidden; border-radius: {border_radius_px}px;">
            <img src="data:image/png;base64,{b64}"
                 style="width: 100%; height: 100%; object-fit: cover; display: block;" />
        </div>
        """,
        unsafe_allow_html=True,
    )

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

# --- Exposure Category (cards) ---
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

    if "exposure_category" not in st.session_state:
        st.session_state["exposure_category"] = "C"

    cols = st.columns(3)
    for col, key in zip(cols, ["B", "C", "D"]):
        with col:
            # fixed-size image (same height for all)
            _fixed_image(exposure_meta[key]["img"], height_px=140, border_radius_px=14)

            st.write(f"**Exposure {key}**")
            st.caption(exposure_meta[key]["label"])

            if st.button(f"Choose {key}", key=f"choose_exposure_{key}"):
                st.session_state["exposure_category"] = key

    exposure = st.session_state["exposure_category"]  # <-- use the card selection
    st.success(f"Selected Exposure {exposure}")
    st.markdown("---")

# --- Kz (placeholder) ---
    def get_kz(h, exp):
        table = {"B": 0.70, "C": 0.98, "D": 1.16}
        return table.get(exp, 1.0)

    Kz = get_kz(height, exposure)
    Kzt = 1.0
    Ke = 1.0

    q = 0.00256 * Kz * Kzt * Kd * Ke * (float(V) ** 2)

    st.metric("Velocity Pressure (q)", f"{q:.2f} psf")
    st.caption(f"Kd={Kd}, Kz={Kz}, Kzt={Kzt}, Ke={Ke}, V={float(V):.1f} mph, h={float(height):.1f} ft")
    st.markdown("---")

    # (Optional) return exposure if you want to use it elsewhere
    return exposure, q
