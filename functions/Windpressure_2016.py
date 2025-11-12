# wind_pressure_module.py
import streamlit as st

def wind_pressure(qh: float, GCp: float, GCpi: float) -> float:
    """
    Compute design wind pressure (p) for Components & Cladding
    per ASCE 7-16 Eq. 30.3-1:
        p = qh * (GCp - GCpi)
    """
    return qh * (GCp - GCpi)


def wind_pressure_ui(qh_default=25.0):
    """
    Streamlit UI block for computing design wind pressure
    with GCpi from Table 26.13-1 (based on enclosure type)
    """

    st.subheader("🌬️ Wind Pressure Calculation (ASCE 7-16 Eq. 30.3-1)")

    qh = st.number_input("Velocity Pressure qh (psf)", value=qh_default, min_value=0.0, format="%.3f")
    GCp = st.number_input("External Pressure Coefficient (GCp)", value=-0.9, step=0.05, format="%.3f")

    # Enclosure classification → GCpi from Table 26.13-1
    enclosure_type = st.selectbox(
        "Enclosure Classification (per Table 26.13-1):",
        ["Open", "Enclosed", "Partially Enclosed"],
        help="Select the building enclosure classification per ASCE 7-16 Table 26.13-1."
    )

    if enclosure_type == "Open":
        GCpi_values = [0.0]
    elif enclosure_type == "Enclosed":
        GCpi_values = [+0.18, -0.18]
    elif enclosure_type == "Partially Enclosed":
        GCpi_values = [+0.55, -0.55]

    st.write(f"**Selected GCpi values:** {GCpi_values}")

    st.markdown("### Results")

    for GCpi in GCpi_values:
        p = wind_pressure(qh, GCp, GCpi)
        st.write(f"- For GCpi = {GCpi:+.2f} →  **p = {p:.2f} psf**")

    st.caption("Per ASCE 7-16 Eq. 30.3-1 and Table 26.13-1")

# Example for standalone Streamlit page
if __name__ == "__main__":
    st.title("ASCE 7-16 Wind Pressure Calculator")
    wind_pressure_ui()
