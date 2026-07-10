import streamlit as st


def internal_pressure():
    """
    Allows the user to select the ASCE 7-16 enclosure classification
    and returns the corresponding internal pressure coefficients, GCpi.

    Returns
    -------
    enclosure_classification : str
        Selected enclosure classification.

    gcpi_positive : float
        Positive internal pressure coefficient.

    gcpi_negative : float
        Negative internal pressure coefficient.
    """

    st.markdown("### Internal Pressure Coefficient, GCpi")

    enclosure_options = [
        "Enclosed Building",
        "Partially Enclosed Building",
        "Partially Open Building",
        "Open Building",
    ]

    enclosure_classification = st.selectbox(
        "Select Enclosure Classification",
        enclosure_options,
        key="enclosure_classification",
    )

    enclosure_data = {
        "Enclosed Building": {
            "internal_pressure": "Moderate",
            "gcpi_positive": 0.18,
            "gcpi_negative": -0.18,
            "criteria": (
                "The total area of openings in each wall and roof, excluding "
                "the dominant wall, does not meet the requirements for a "
                "partially enclosed or open building."
            ),
        },
        "Partially Enclosed Building": {
            "internal_pressure": "High",
            "gcpi_positive": 0.55,
            "gcpi_negative": -0.55,
            "criteria": (
                "The building has a dominant opening and satisfies the "
                "ASCE 7 requirements for a partially enclosed building."
            ),
        },
        "Partially Open Building": {
            "internal_pressure": "Moderate",
            "gcpi_positive": 0.18,
            "gcpi_negative": -0.18,
            "criteria": (
                "The building does not comply with the enclosed, partially "
                "enclosed, or open building classifications."
            ),
        },
        "Open Building": {
            "internal_pressure": "Negligible",
            "gcpi_positive": 0.00,
            "gcpi_negative": 0.00,
            "criteria": "Each wall is at least 80% open.",
        },
    }

    selected_data = enclosure_data[enclosure_classification]

    gcpi_positive = selected_data["gcpi_positive"]
    gcpi_negative = selected_data["gcpi_negative"]

    st.info(
        f"**Classification criteria:** {selected_data['criteria']}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Internal Pressure",
            value=selected_data["internal_pressure"],
        )

    with col2:
        st.metric(
            label="Positive GCpi",
            value=f"{gcpi_positive:+.2f}",
        )

    with col3:
        st.metric(
            label="Negative GCpi",
            value=f"{gcpi_negative:+.2f}",
        )

    st.caption(
        "Positive and negative GCpi cases should be evaluated separately "
        "to determine the governing design pressure."
    )

    return enclosure_classification, gcpi_positive, gcpi_negative

