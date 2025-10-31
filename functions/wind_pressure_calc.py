import streamlit as st

def wind_pressure_calc(height, V):
    st.header("5️⃣ Basic Wind Pressure Calculation (ASCE 7-16)")

    structure_types = {
        "Main Wind Force Resisting System (Buildings)": 0.85,
        "Components and Cladding": 0.85,
        "Circular Domes": 1.0,
        "Chimneys / Tanks (Round)": 1.0
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
