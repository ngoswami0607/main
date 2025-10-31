import streamlit as st
import requests
import pdfplumber
import pandas as pd
import io
import re

@st.cache_data(show_spinner=True)
def load_icc_table_pdfplumber():
    PDF_URL = "https://www.iccsafe.org/wp-content/uploads/Master-I-Code-Adoption-Chart-1.pdf"
    response = requests.get(PDF_URL)
    response.raise_for_status()

    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # Extract lines that look like state rows
    states = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana",
        "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts",
        "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
        "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
        "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
        "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
        "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
    ]

    states_data = []
    lines = text.split("\n")
    current_state = None
    buffer = ""

    for line in lines:
        if any(line.startswith(s) for s in states):
            if current_state and buffer.strip():
                states_data.append([current_state, buffer.strip()])
            current_state = line.split(" ")[0]
            buffer = line[len(current_state):].strip()
        else:
            buffer += " " + line.strip()

    if current_state and buffer.strip():
        states_data.append([current_state, buffer.strip()])

    df = pd.DataFrame(states_data, columns=["State", "Code Info"])
    return df


def extract_relevant_codes(code_text):
    """
    Extract IBC, ASCE 7, IECC, and ASHRAE codes from text.
    """
    text = code_text.upper().replace("–", "-").replace("—", "-")

    building_code = ibc_code = asce_code = iecc_code = ashrae_code = ""

    ibc_match = re.search(r"IBC\s*(19|20)\d{2}", text)
    asce_match = re.search(r"ASCE\s*7[-–]\s*(\d{2})", text)
    iecc_match = re.search(r"IECC\s*(19|20)\d{2}", text)
    ashrae_match = re.search(r"(ASHRAE|90\.1)[-\s]*(19|20)\d{2}", text)

    if ibc_match:
        ibc_code = f"IBC {ibc_match.group(0).split()[-1]}"
    if asce_match:
        asce_code = f"ASCE 7-{asce_match.group(1)}"
    if iecc_match:
        iecc_code = f"IECC {iecc_match.group(0).split()[-1]}"
    if ashrae_match:
        ashrae_code = f"ASHRAE 90.1-{ashrae_match.group(2)}"
    if ibc_code:
        building_code = ibc_code

    # --- Fallback: numeric-only format ---
    if not any([ibc_code, asce_code, iecc_code, ashrae_code]):
        years = re.findall(r'\b(0[9]|1[0-9]|2[0-5])\b', text)
        if len(years) >= 1:
            ibc_code = f"IBC 20{years[0]}"
            building_code = f"Building Code 20{years[0]}"
        if len(years) >= 2:
            asce_code = f"ASCE 7-20{years[1]}"
        if len(years) >= 3:
            iecc_code = f"IECC 20{years[2]}"
        if len(years) >= 4:
            ashrae_code = f"ASHRAE 90.1-20{years[3]}"

    return building_code, ibc_code, asce_code, iecc_code, ashrae_code


# --- Main display function ---
def code_jurisdiction():
    st.title("US State Building Code Finder 🏗️")
    st.markdown("This tool retrieves the latest **ICC Building Code adoption data** and extracts key code information for each U.S. state.")

    with st.spinner("Loading ICC adoption data..."):
        df_codes = load_icc_table_pdfplumber()

    state_list = sorted(df_codes["State"].unique())
    selected_state = st.selectbox("Select a U.S. State:", state_list)

    state_info = df_codes[df_codes["State"] == selected_state]
    if not state_info.empty:
        code_text = state_info.iloc[0]["Code Info"]
        building_code, ibc_code, asce_code, iecc_code, ashrae_code = extract_relevant_codes(code_text)

        st.markdown("### 🔍 Parsed Code References")
        st.write(f"**Building Code:** {building_code or 'N/A'}")
        st.write(f"**IBC Reference:** {ibc_code or 'N/A'}")
        st.write(f"**ASCE 7 Edition:** {asce_code or 'N/A'}")
        st.write(f"**IECC Edition:** {iecc_code or 'N/A'}")
        st.write(f"**ASHRAE 90.1 Edition:** {ashrae_code or 'N/A'}")
    else:
        st.warning("State not found in the ICC dataset.")

    st.markdown("---")
    st.caption("Data Source: [ICC Master I-Code Adoption Chart](https://www.iccsafe.org/wp-content/uploads/Master-I-Code-Adoption-Chart-1.pdf)")
