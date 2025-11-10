import requests
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI()

def fetch_icc_codes(location: str) -> str:
    """
    Fetches IBC and IECC code information for a given location
    from the ICC Digital Codes website using an LLM.
    
    Parameters
    ----------
    location : str
        U.S. state or country name (e.g., "Wisconsin", "Texas", "Canada")
    
    Returns
    -------
    str
        LLM-summarized information on IBC and IECC adoption for that location.
    """
    base_url = "https://codes.iccsafe.org/"
    search_url = f"{base_url}?q={location.replace(' ', '%20')}"

    # Step 1: Try to fetch webpage content
    try:
        response = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except Exception as e:
        return f"❌ Could not fetch data from ICC website: {e}"

    # Step 2: Extract readable content
    soup = BeautifulSoup(response.text, "html.parser")
    text_content = soup.get_text(separator="\n", strip=True)

    # Step 3: LLM summarization prompt
    prompt = f"""
    You are an engineering assistant helping identify the adopted building codes.
    Given the ICC Digital Codes text for '{location}', determine:
    - The current International Building Code (IBC) edition.
    - The current International Energy Conservation Code (IECC) edition.
    - Any relevant notes or local amendments.

    Format response clearly:
    IBC: [edition or year]
    IECC: [edition or year]
    Notes: [short remarks if applicable]

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
