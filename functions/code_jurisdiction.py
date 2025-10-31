import streamlit as st
import pdfplumber, requests, io, pandas as pd, re

@st.cache_data
def load_icc_pdf():
    url = "https://www.iccsafe.org/wp-content/uploads/Master-I-Code-Adoption-Chart-1.pdf"
    r = requests.get(url)
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        text = "\n".join([p.extract_text() for p in pdf.pages])
    return text

def extract_asce_code(text):
    match = re.search(r"ASCE\s*7[-–]\s*(\d{2})", text.upper())
    return f"ASCE 7-{match.group(1)}" if match else "N/A"

def code_jurisdiction():
    st.header("2️⃣ Code Jurisdiction Lookup")
    st.markdown("Retrieve current code adoption info from ICC.")

    with st.spinner("Loading ICC data..."):
        text = load_icc_pdf()

    state = st.text_input("Enter U.S. state:", "California")
    lines = [l for l in text.splitlines() if l.strip().startswith(state)]
    selected_text = lines[0] if lines else "No data found."

    asce_code = extract_asce_code(selected_text)
    st.success(f"Detected {asce_code} for {state}")
    st.markdown("---")
    return asce_code

