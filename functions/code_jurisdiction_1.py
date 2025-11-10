import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# --- Initialize OpenAI Client ---
client = OpenAI()

# --- Define helper function for ICC Code search ---
def get_icc_codes(location: str):
    """
    Searches ICC Digital Codes website for IBC and IECC references
    using LLM summarization.
    """
    base_url = "https://codes.iccsafe.org/"
    search_url = f"{base_url}?q={location.replace(' ', '%20')}"

    try:
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except Exception as e:
        return f"❌ Could not fetch data from ICC website: {e}"

    # Extract readable text
    soup = BeautifulSoup(response.text, "html.parser")
    text_content = soup.get_text(separator="\n", strip=True)

    # Prepare LLM prompt
    prompt = f"""
    You are helping an engineer determine which International Building Code (IBC)
    and International Energy Conservation Code (IECC) editions are adopted in the
    following location: {location}.
    Analyze the ICC website text below and extract the most relevant code editions.

    Respond in this format:
    - IBC: [year or edition]
    - IECC: [year or edition]
    - Notes: [any key local amendment or note]
    
    Website text:
    {text_content[:8000]}
    """

    try:
        llm_response = client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return llm_response.choices[0].message.content
    except Exception as e:
        return f"⚠️ LLM query failed: {e}"


# --- Streamlit Integration ---
st.title("🌪️ Wind Load Calculator (ASCE 7)")

# Step: Get user input location
st.subheader("Step 1: Enter Project Location")
location = st.text_input("Enter location (e.g., Wisconsin, Texas, Canada)")

# Optional button to query ICC Codes
if st.button("🔍 Fetch ICC Code Information"):
    with st.spinner(f"Fetching IBC and IECC data for {location}..."):
        if location.strip() == "":
            st.warning("Please enter a valid location name.")
        else:
            code_info = get_icc_codes(location)
            st.markdown("### 📘 Applicable Codes:")
            st.markdown(code_info)

# Rest of your wind load app logic below (e.g., Step 2 onwards)
# ...

