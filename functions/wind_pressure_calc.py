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

# --- Compute Kz from Table 26.10-1 ---
def get_kz(height_ft, exposure):
    # Table 26.10-1 (ASCE 7-16)
    table = {
        "B": {15: 0.57, 20: 0.62, 25: 0.66, 30: 0.70, 40: 0.76, 50: 0.81, 60: 0.85, 70: 0.89, 80: 0.93, 90: 0.96, 100: 0.99, 120: 1.04, 140: 1.09, 160: 1.13, 200: 1.20, 250: 1.28, 300: 1.35, 350: 1.41, 400: 1.47, 450: 1.52, 500: 1.56},
        "C": {15: 0.85, 20: 0.90, 25: 0.94, 30: 0.98, 40: 1.04, 50: 1.09, 60: 1.13, 70: 1.17, 80: 1.21, 90: 1.24, 100: 1.26, 120: 1.31, 140: 1.36, 160: 1.39, 200: 1.46, 250: 1.53, 300: 1.59, 350: 1.64, 400: 1.69, 450: 1.73, 500: 1.77},
        "D": {15: 1.03, 20: 1.08, 25: 1.12, 30: 1.16, 40: 1.22, 50: 1.27, 60: 1.31, 70: 1.34, 80: 1.38, 90: 1.40, 100: 1.43, 120: 1.48, 140: 1.52, 160: 1.55, 200: 1.61, 250: 1.68, 300: 1.73, 350: 1.78, 400: 1.82, 450: 1.86, 500: 1.89}
    }

    h = min(max(height_ft, 15), 500)
    heights = sorted(table[exposure].keys())

    # Linear interpolation
    for i in range(len(heights)-1):
        h1, h2 = heights[i], heights[i+1]
        if h1 <= h <= h2:
            k1, k2 = table[exposure][h1], table[exposure][h2]
            return k1 + (k2 - k1) * ((h - h1) / (h2 - h1))
    
    Kz = get_kz(height, exposure)
    st.success(f"Kz (at {height:.1f} ft, Exposure {exposure}) = **{Kz:.3f}**")

    st.metric(
    label=f"Kz (Exposure {exposure}, h = {height:.0f} ft)",
    value=f"{Kz:.3f}"    )

    # --- Constants ---
    Kzt = 1.0
    Ke = 1.0

    q = 0.00256 * Kz * Kzt * Kd * Ke * (float(V) ** 2)

    st.metric("Velocity Pressure (q)", f"{q:.2f} psf")
    st.caption(f"Kd={Kd}, Kz={Kz}, Kzt={Kzt}, Ke={Ke}, V={float(V):.1f} mph, h={float(height):.1f} ft")
    st.markdown("---")

    # (Optional) return exposure if you want to use it elsewhere
    return exposure, q
