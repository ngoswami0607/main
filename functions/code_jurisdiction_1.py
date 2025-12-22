from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup
import streamlit as st


ICC_US_CODES_URL = "https://codes.iccsafe.org/codes/united-states"

STATE_OPTIONS = [
    ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"),
    ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"),
    ("DE", "Delaware"), ("DC", "District of Columbia"), ("FL", "Florida"),
    ("GA", "Georgia"), ("HI", "Hawaii"), ("ID", "Idaho"), ("IL", "Illinois"),
    ("IN", "Indiana"), ("IA", "Iowa"), ("KS", "Kansas"), ("KY", "Kentucky"),
    ("LA", "Louisiana"), ("ME", "Maine"), ("MD", "Maryland"),
    ("MA", "Massachusetts"), ("MI", "Michigan"), ("MN", "Minnesota"),
    ("MS", "Mississippi"), ("MO", "Missouri"), ("MT", "Montana"),
    ("NE", "Nebraska"), ("NV", "Nevada"), ("NH", "New Hampshire"),
    ("NJ", "New Jersey"), ("NM", "New Mexico"), ("NY", "New York"),
    ("NC", "North Carolina"), ("ND", "North Dakota"), ("OH", "Ohio"),
    ("OK", "Oklahoma"), ("OR", "Oregon"), ("PA", "Pennsylvania"),
    ("RI", "Rhode Island"), ("SC", "South Carolina"),
    ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"),
    ("UT", "Utah"), ("VT", "Vermont"), ("VA", "Virginia"),
    ("WA", "Washington"), ("WV", "West Virginia"),
    ("WI", "Wisconsin"), ("WY", "Wyoming"),
]

@dataclass
class CodeAdoptionResult:
    state_name: str
    state_url: str
    ibc_year: Optional[int]
    iecc_year: Optional[int]


def _http_get(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WindLoadCalculator/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.text


def _normalize_state(state_input: str) -> str:
    s = (state_input or "").strip()
    if not s:
        raise ValueError("State is required.")
    s_up = s.upper()
    if len(s_up) == 2 and s_up in STATE_ABBR_TO_NAME:
        return STATE_ABBR_TO_NAME[s_up]
    return s.title()


def _build_state_link_map(us_codes_html: str) -> Dict[str, str]:
    """
    Build a mapping of state-like link texts to their URLs from the ICC US codes page.
    We store multiple keys per link:
      - "Wisconsin"
      - "Wisconsin Codes"
    so matching is easy.
    """
    soup = BeautifulSoup(us_codes_html, "html.parser")
    links: Dict[str, str] = {}

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        txt = (a.get_text() or "").strip()
        if not txt:
            continue

        # Only keep ICC /codes/* links
        if not href.startswith("/codes/"):
            continue

        # Ignore the US landing page itself
        if href.startswith("/codes/united-states"):
            continue

        url = "https://codes.iccsafe.org" + href

        # Save multiple normalized keys
        key1 = txt.strip()
        key2 = txt.replace("Codes", "").strip()  # "Wisconsin Codes" -> "Wisconsin"
        links[key1.lower()] = url
        if key2:
            links[key2.lower()] = url

    return links


def _extract_code_year_from_text(text: str, code_name: str) -> Optional[int]:
    """
    Find a year near code_name in visible text.
    We scan short windows around occurrences and select the most recent year found.
    """
    candidates = []
    for m in re.finditer(re.escape(code_name), text, flags=re.IGNORECASE):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 200)
        snippet = text[start:end]
        years = re.findall(r"\b(19\d{2}|20\d{2})\b", snippet)
        candidates.extend(int(y) for y in years)

    candidates = [y for y in candidates if 1990 <= y <= 2099]
    return max(candidates) if candidates else None


def lookup_icc_state_adoption(state: str) -> CodeAdoptionResult:
    state_name = _normalize_state(state)

    us_html = _http_get(ICC_US_CODES_URL)
    link_map = _build_state_link_map(us_html)

    # robust match (exact lower first)
    state_url = link_map.get(state_name.lower())

    # fallback: contains match (e.g., "wisconsin" inside "wisconsin codes")
    if not state_url:
        for k, v in link_map.items():
            if state_name.lower() in k:
                state_url = v
                break

    if not state_url:
        raise ValueError(f"State link not found on ICC page for: {state_name}")

    state_html = _http_get(state_url)
    soup = BeautifulSoup(state_html, "html.parser")
    visible_text = soup.get_text(" ", strip=True)

    ibc_year = _extract_code_year_from_text(visible_text, "International Building Code")
    iecc_year = _extract_code_year_from_text(visible_text, "International Energy Conservation Code")

    return CodeAdoptionResult(
        state_name=state_name,
        state_url=state_url,
        ibc_year=ibc_year,
        iecc_year=iecc_year,
    )


def code_jurisdiction_1():
    st.header("3️⃣ Code Jurisdiction / Project Location")

    city = st.text_input("City", value="Milwaukee")

    # --- State dropdown ---
    state_labels = [f"{abbr} – {name}" for abbr, name in STATE_OPTIONS]
    default_index = [abbr for abbr, _ in STATE_OPTIONS].index("WI")

    state_choice = st.selectbox(
        "State",
        options=state_labels,
        index=default_index,
    )

    state_abbr = state_choice.split("–")[0].strip()

    ibc_year = None
    iecc_year = None
    source_url = None

    # --- ICC lookup ---
    try:
        res = lookup_icc_state_adoption(state_abbr)
        ibc_year = res.ibc_year
        iecc_year = res.iecc_year
        source_url = res.state_url

        st.success("ICC state adoption found.")
        if source_url:
            st.caption(f"Source: {source_url}")

    except Exception as e:
        st.warning("ICC lookup failed — enter years manually.")
        with st.expander("Show lookup error"):
            st.code(str(e))

    # --- Manual override ---
    col1, col2 = st.columns(2)
    with col1:
        ibc_in = st.text_input(
            "IBC Year",
            value=str(ibc_year) if ibc_year else "",
            placeholder="e.g. 2021",
        )
    with col2:
        iecc_in = st.text_input(
            "IECC Year",
            value=str(iecc_year) if iecc_year else "",
            placeholder="e.g. 2018",
        )

    st.markdown("---")

    return {
        "city": city,
        "state": state_abbr,
        "ibc_year": int(ibc_in) if ibc_in.isdigit() else ibc_year,
        "iecc_year": int(iecc_in) if iecc_in.isdigit() else iecc_year,
        "source": source_url,
    }
