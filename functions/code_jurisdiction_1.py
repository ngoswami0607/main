from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

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
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://codes.iccsafe.org/",
    }
    r = requests.get(url, headers=headers, timeout=25)
    r.raise_for_status()
    return r.text


def _state_slug(state_name: str) -> str:
    return state_name.strip().lower().replace(" ", "-")


def _find_next_data_json(html: str) -> Optional[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return None
    try:
        return json.loads(tag.string)
    except Exception:
        return None


def _walk(obj: Any):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k, v
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def _extract_year_from_title_string(s: str) -> Optional[int]:
    """
    Extract a 4-digit year from strings like:
      '2021 International Building Code (IBC)'
    """
    m = re.search(r"\b(19\d{2}|20\d{2})\b", s)
    return int(m.group(1)) if m else None


def _extract_years_from_next_data(next_data: Dict[str, Any]) -> Dict[str, Optional[int]]:
    ibc_year = None
    iecc_year = None

    strings = []
    for _, v in _walk(next_data):
        if isinstance(v, str):
            strings.append(v)

    for s in strings:
        s_low = s.lower()

        if ibc_year is None and ("international building code" in s_low and "(ibc)" in s_low):
            y = _extract_year_from_title_string(s)
            if y:
                ibc_year = y

        if iecc_year is None and ("international energy conservation code" in s_low and "(iecc)" in s_low):
            y = _extract_year_from_title_string(s)
            if y:
                iecc_year = y

        if ibc_year and iecc_year:
            break

    return {"ibc_year": ibc_year, "iecc_year": iecc_year}


def _fallback_extract_from_visible_text(html: str) -> Dict[str, Optional[int]]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    def near(anchor: str) -> Optional[int]:
        candidates = []
        for m in re.finditer(re.escape(anchor), text, flags=re.IGNORECASE):
            start = max(0, m.start() - 250)
            end = min(len(text), m.end() + 250)
            snippet = text[start:end]
            years = re.findall(r"\b(19\d{2}|20\d{2})\b", snippet)
            candidates.extend(int(y) for y in years)
        candidates = [y for y in candidates if 1990 <= y <= 2099]
        return max(candidates) if candidates else None

    return {
        "ibc_year": near("International Building Code (IBC)"),
        "iecc_year": near("International Energy Conservation Code (IECC)"),
    }


def lookup_icc_state_adoption_by_slug(state_abbr: str) -> CodeAdoptionResult:
    abbr = (state_abbr or "").strip().upper()
    if abbr not in STATE_ABBR_TO_NAME:
        raise ValueError(f"Unknown state abbreviation: {abbr}")

    state_name = STATE_ABBR_TO_NAME[abbr]
    url = ICC_STATE_URL_TEMPLATE.format(slug=_state_slug(state_name))

    html = _http_get(url)

    next_data = _find_next_data_json(html)
    if next_data:
        yrs = _extract_years_from_next_data(next_data)
        ibc_year = yrs["ibc_year"]
        iecc_year = yrs["iecc_year"]
    else:
        yrs = _fallback_extract_from_visible_text(html)
        ibc_year = yrs["ibc_year"]
        iecc_year = yrs["iecc_year"]

    return CodeAdoptionResult(
        state_abbr=abbr,
        state_name=state_name,
        state_url=url,
        ibc_year=ibc_year,
        iecc_year=iecc_year,
    )


def debug_icc_raw_html(url: str) -> None:
    """
    Call this from the UI when lookup fails.
    It will tell you whether the HTML you got actually contains the code titles or __NEXT_DATA__.
    """
    html = _http_get(url)

    st.write("### ICC Raw HTML Debug")
    st.write("HTML length:", len(html))

    probes = [
        "International Building Code",
        "International Energy Conservation Code",
        "(IBC)",
        "(IECC)",
        "__NEXT_DATA__",
        "pageProps",
    ]
    for p in probes:
        st.write(f"`{p}` present?", p in html)

    st.code(html[:1500])


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
    err = None

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
        err = str(e)
        st.warning("ICC lookup failed — enter years manually.")

    if err:
        with st.expander("Show lookup error / debug"):
            st.code(err)
            if source_url:
                st.write("Running raw HTML debug:")
                debug_icc_raw_html(source_url)

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
        "source": source_url,
    }
