from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List

import requests
from bs4 import BeautifulSoup
import streamlit as st


# --- State options (same as you already have) ---
STATE_OPTIONS: List[Tuple[str, str]] = [
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
STATE_ABBR_TO_NAME: Dict[str, str] = dict(STATE_OPTIONS)


@dataclass
class AdoptionYears:
    ibc_year: Optional[int]
    iecc_year: Optional[int]
    source_url: str
    state_name: str


def _http_get(url: str, timeout_s: int = 25) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WindLoadCalculator/1.0)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = requests.get(url, headers=headers, timeout=timeout_s)
    r.raise_for_status()
    return r.text


def _state_slug_for_adoptions(state_name: str) -> str:
    # ICC advocacy adoption map uses lowercase + hyphens (works for most states)
    return state_name.strip().lower().replace(" ", "-")


def _extract_year_near(text: str, anchors: List[str], window: int = 250) -> Optional[int]:
    """
    Finds the most recent (max) year within a window around any anchor phrase.
    """
    years: List[int] = []
    for anchor in anchors:
        for m in re.finditer(re.escape(anchor), text, flags=re.IGNORECASE):
            s = max(0, m.start() - window)
            e = min(len(text), m.end() + window)
            snippet = text[s:e]
            hits = re.findall(r"\b(19\d{2}|20\d{2})\b", snippet)
            years.extend(int(y) for y in hits)

    years = [y for y in years if 1990 <= y <= 2099]
    return max(years) if years else None


def lookup_state_ibc_iecc_from_iccsafe_adoptions(state_abbr: str, debug: bool = False) -> AdoptionYears:
    abbr = (state_abbr or "").strip().upper()
    if abbr not in STATE_ABBR_TO_NAME:
        raise ValueError(f"Unknown state abbreviation: {abbr}")

    state_name = STATE_ABBR_TO_NAME[abbr]
    slug = _state_slug_for_adoptions(state_name)

    # ✅ Server-rendered adoption page (example exists for Illinois).  :contentReference[oaicite:1]{index=1}
    url = f"https://www.iccsafe.org/advocacy/adoptions-map/{slug}/"

    html = _http_get(url)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
"""
    if debug:
        with st.expander("🔎 Adoption page debug"):
            st.write("URL:", url)
            st.write("HTML length:", len(html))
            st.write("Contains 'IECC'?", "IECC" in text)
            st.write("Contains 'IBC'?", "IBC" in text)
            st.code(text[:1200])
"""
    # These anchors match how ICC commonly writes it on the adoption pages (e.g., “2018 IECC”, “2015 IBC”). :contentReference[oaicite:2]{index=2}
    ibc_year = _extract_year_near(text, anchors=[" IBC", "International Building Code"], window=180)
    iecc_year = _extract_year_near(text, anchors=[" IECC", "International Energy Conservation Code"], window=180)

    return AdoptionYears(
        ibc_year=ibc_year,
        iecc_year=iecc_year,
        source_url=url,
        state_name=state_name,
    )


def code_jurisdiction_1() -> Dict[str, object]:
    st.header("3️⃣ Code Jurisdiction / Project Location")

    city = st.text_input("City", value="Milwaukee")

    # --- State dropdown ---
    state_labels = [f"{abbr} – {name}" for abbr, name in STATE_OPTIONS]
    default_index = [abbr for abbr, _ in STATE_OPTIONS].index("WI")
    state_choice = st.selectbox("State", options=state_labels, index=default_index)
    state_abbr = state_choice.split("–")[0].strip()

    ibc_year: Optional[int] = None
    iecc_year: Optional[int] = None
    source_url: Optional[str] = None
    err: Optional[str] = None

    try:
        res = lookup_state_ibc_iecc_from_iccsafe_adoptions(state_abbr, debug=True)
        ibc_year = res.ibc_year
        iecc_year = res.iecc_year
        source_url = res.source_url
        st.caption(f"Source: {source_url}")
    except Exception as e:
        err = str(e)
        st.warning("Auto-lookup failed — enter years manually.")
        with st.expander("Show lookup error"):
            st.code(err)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("IBC (State)", str(ibc_year) if ibc_year else "Not found")
    with c2:
        st.metric("IECC (State)", str(iecc_year) if iecc_year else "Not found")

    col1, col2 = st.columns(2)
    with col1:
        ibc_in = st.text_input("IBC Year", value=str(ibc_year) if ibc_year else "", placeholder="e.g. 2021")
    with col2:
        iecc_in = st.text_input("IECC Year", value=str(iecc_year) if iecc_year else "", placeholder="e.g. 2018")

    st.markdown("---")
    return {
        "city": city,
        "state": state_abbr,
        "ibc_year": int(ibc_in) if ibc_in.isdigit() else ibc_year,
        "iecc_year": int(iecc_in) if iecc_in.isdigit() else iecc_year,
        "source_url": source_url,
        "error": err,
    }
