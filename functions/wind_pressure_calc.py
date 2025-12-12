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

    exposure = st.selectbox("Exposure Category:", ["B", "C", "D"], index=1)

    def get_kz(h, exposure):
        table = {"B": 0.70, "C": 0.98, "D": 1.16}
        return table.get(exposure, 1.0)

    Kz = get_kz(height, exposure)
    Kzt, Ke = 1.0, 1.0
    q = 0.00256 * Kz * Kzt * Kd * Ke * (V ** 2)

    st.metric(label="Velocity Pressure (q)", value=f"{q:.2f} psf")
    st.markdown("---")
