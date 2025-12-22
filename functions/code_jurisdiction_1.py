from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple

import requests
from bs4 import BeautifulSoup
import streamlit as st


ICC_STATE_URL_TEMPLATE = "https://codes.iccsafe.org/codes/{slug}"  # ✅ FIXED

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
class CodeAdoptionResult:
    state_abbr: str
    state_name: str
    state_url: str
    ibc_year: Optional[int]
    iecc_year: Optional[int]


def _http_get(url: str, timeout_s: int = 25) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WindLoadCalculator/1.0)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://codes.iccsafe.org/",
    }
    r = requests.get(url, headers=headers, timeout=timeout_s)
    r.raise_for_status()
    return r.text


def _state_slug(state_name: str) -> str:
    # Matches ICC slugs like "district-of-columbia"
    return state_name.strip().lower().replace(" ", "-")


def _extract_code_year_from_visible_text(html: str, code_name: str) -> Optional[int]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    candidates: list[int] = []
    for m in re.finditer(re.escape(code_name), text, flags=re.IGNORECASE):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 200)
        snippet = text[start:end]
        years = re.findall(r"\b(19\d{2}|20\d{2})\b", snippet)
        candidates.extend(int(y) for y in years)

    candidates = [y for y in candidates if 1990 <= y <= 2099]
    return max(candidates) if candidates else None


def lookup_icc_state_adoption(state_abbr: str, debug_ui: bool = False) -> CodeAdoptionResult:
    abbr = (state_abbr or "").strip().upper()
    if abbr not in STATE_ABBR_TO_NAME:
        raise ValueError(f"Unknown state abbreviation: {abbr}")

    state_name = STATE_ABBR_TO_NAME[abbr]
    slug = _state_slug(state_name)

    # ✅ FIXED URL
    state_url = ICC_STATE_URL_TEMPLATE.format(slug=slug)

    html = _http_get(state_url)

    if debug_ui:
        with st.expander("🔎 ICC HTML debug"):
            st.write("State URL:", state_url)
            st.write("HTML length:", len(html))
            st.write("Contains 'International Building Code'?", "International Building Code" in html)
            st.write("Contains 'International Energy Conservation Code'?", "International Energy Conservation Code" in html)
            st.code(html[:1500])

    ibc_year = _extract_code_year_from_visible_text(html, "International Building Code")
    iecc_year = _extract_code_year_from_visible_text(html, "International Energy Conservation Code")

    return CodeAdoptionResult(
        state_abbr=abbr,
        state_name=state_name,
        state_url=state_url,
        ibc_year=ibc_year,
        iecc_year=iecc_year,
    )


def code_jurisdiction_1() -> Dict[str, Any]:
    st.header("3️⃣ Code Jurisdiction / Project Location")

    city = st.text_input("City", value="Milwaukee")

    state_labels = [f"{abbr} – {name}" for abbr, name in STATE_OPTIONS]
    default_index = [abbr for abbr, _ in STATE_OPTIONS].index("WI")
    state_choice = st.selectbox("State", options=state_labels, index=default_index)
    state_abbr = state_choice.split("–")[0].strip()

    ibc_year = None
    iecc_year = None
    source_url = None
    err = None

    try:
        res = lookup_icc_state_adoption(state_abbr, debug_ui=True)  # set to False once stable
        ibc_year = res.ibc_year
        iecc_year = res.iecc_year
        source_url = res.state_url
        st.success("ICC state page found.")
        st.caption(f"Source: {source_url}")
    except Exception as e:
        err = str(e)
        st.warning("ICC lookup failed — enter years manually.")
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
