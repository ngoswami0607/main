from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

import requests
from bs4 import BeautifulSoup
import streamlit as st


ICC_STATE_URL_TEMPLATE = "https://codes.iccsafe.org/codes/united-states/{slug}"

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

STATE_ABBR_TO_NAME: Dict[str, str] = dict(STATE_OPTIONS)


@dataclass
class CodeAdoptionResult:
    state_abbr: str
    state_name: str
    state_url: str
    ibc_year: Optional[int]
    iecc_year: Optional[int]


def _http_get(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WindLoadCalculator/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }
    r = requests.get(url, headers=headers, timeout=25)
    r.raise_for_status()
    return r.text


def _state_slug(state_name: str) -> str:
    """
    ICC uses lowercase slugs with hyphens.
    Example: "West Virginia" -> "west-virginia"
             "Wisconsin" -> "wisconsin"
    """
    return state_name.strip().lower().replace(" ", "-")


def _extract_year_near(text: str, anchor: str) -> Optional[int]:
    """
    Find a 4-digit year near an anchor phrase.
    We'll grab a short window around each match and pick the most recent year.
    """
    candidates = []
    for m in re.finditer(re.escape(anchor), text, flags=re.IGNORECASE):
        start = max(0, m.start() - 120)
        end = min(len(text), m.end() + 120)
        snippet = text[start:end]
        for y in re.findall(r"\b(19\d{2}|20\d{2})\b", snippet):
            candidates.append(int(y))
    candidates = [y for y in candidates if 1990 <= y <= 2099]
    return max(candidates) if candidates else None


def lookup_icc_state_adoption_by_slug(state_abbr: str) -> CodeAdoptionResult:
    abbr = (state_abbr or "").strip().upper()
    if abbr not in STATE_ABBR_TO_NAME:
        raise ValueError(f"Unknown state abbreviation: {abbr}")

    state_name = STATE_ABBR_TO_NAME[abbr]
    slug = _state_slug(state_name)
    url = ICC_STATE_URL_TEMPLATE.format(slug=slug)

    html = _http_get(url)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    # These anchors match what your screenshot shows:
    # "2021 International Building Code (IBC)"
    # "2021 International Energy Conservation Code (IECC)"
    ibc_year = _extract_year_near(text, "International Building Code (IBC)")
    if ibc_year is None:
        ibc_year = _extract_year_near(text, "International Building Code")

    iecc_year = _extract_year_near(text, "International Energy Conservation Code (IECC)")
    if iecc_year is None:
        iecc_year = _extract_year_near(text, "International Energy Conservation Code")

    return CodeAdoptionResult(
        state_abbr=abbr,
        state_name=state_name,
        state_url=url,
        ibc_year=ibc_year,
        iecc_year=iecc_year,
    )


def code_jurisdiction_1():
    st.header("3️⃣ Code Jurisdiction / Project Location")

    city = st.text_input("City", value="Milwaukee")

    state_labels = [f"{abbr} – {name}" for abbr, name in STATE_OPTIONS]
    default_index = [abbr for abbr, _ in STATE_OPTIONS].index("WI")

    state_choice = st.selectbox("State", state_labels, index=default_index)
    state_abbr = state_choice.split("–")[0].strip()

    ibc_year = None
    iecc_year = None
    source_url = None

    try:
        res = lookup_icc_state_adoption_by_slug(state_abbr)
        ibc_year = res.ibc_year
        iecc_year = res.iecc_year
        source_url = res.state_url

        st.success("ICC state adoption found.")
        st.caption(f"Source: {source_url}")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("IBC (State)", str(ibc_year) if ibc_year else "Not found")
        with c2:
            st.metric("IECC (State)", str(iecc_year) if iecc_year else "Not found")

    except Exception as e:
        st.warning("ICC lookup failed — enter years manually.")
        with st.expander("Show lookup error"):
            st.code(str(e))

    # Manual override (always available)
    col1, col2 = st.columns(2)
    with col1:
        ibc_in = st.text_input("IBC Year (manual override)", value=str(ibc_year) if ibc_year else "", placeholder="e.g. 2021")
    with col2:
        iecc_in = st.text_input("IECC Year (manual override)", value=str(iecc_year) if iecc_year else "", placeholder="e.g. 2018")

    st.markdown("---")
    return {
        "city": city,
        "state": state_abbr,
        "ibc_year": int(ibc_in) if ibc_in.isdigit() else ibc_year,
        "iecc_year": int(iecc_in) if iecc_in.isdigit() else iecc_year,
        "source": source_url,
    }
