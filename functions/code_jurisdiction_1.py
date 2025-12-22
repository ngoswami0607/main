# ✅ Why your current “debugging” shows NOT FOUND
# Your debug is correct — it proves the problem:
# - The HTML you get from `requests.get()` is a JS shell (no code titles in the HTML)
# - No "__NEXT_DATA__" script tag is present
# - So searching raw HTML for “International Building Code” will always return False
#
# ✅ Fix: ICC is a Next.js site. The data is usually available at:
#   https://codes.iccsafe.org/_next/data/<BUILD_ID>/codes/united-states/<state-slug>.json
#
# Plan:
# 1) GET the state page HTML
# 2) Extract BUILD_ID from "/_next/static/<BUILD_ID>/_buildManifest.js"
# 3) GET the JSON endpoint above
# 4) Parse the JSON for titles like: "2021 International Building Code (IBC)"

# ------------------------------------------------------------
# functions/code_jurisdiction_1.py  (DROP-IN REPLACEMENT)
# ------------------------------------------------------------

from __future__ import annotations

import re
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple

import requests
import streamlit as st


ICC_HOST = "https://codes.iccsafe.org"
STATE_PAGE_TEMPLATE = ICC_HOST + "/codes/united-states/{slug}"
NEXT_DATA_TEMPLATE = ICC_HOST + "/_next/data/{build_id}/codes/united-states/{slug}.json"

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


def _slugify_state_name(state_name: str) -> str:
    # "District of Columbia" -> "district-of-columbia"
    return state_name.strip().lower().replace(" ", "-")


def _http_get(url: str, timeout_s: int = 25) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WindLoadCalculator/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://codes.iccsafe.org/",
    }
    r = requests.get(url, headers=headers, timeout=timeout_s)
    r.raise_for_status()
    return r.text


def _http_get_json(url: str, timeout_s: int = 25) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WindLoadCalculator/1.0)",
        "Accept": "application/json,text/plain,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://codes.iccsafe.org/",
    }
    r = requests.get(url, headers=headers, timeout=timeout_s)
    r.raise_for_status()
    return r.json()


def _extract_build_id(html: str) -> Optional[str]:
    # Next.js build id typically appears in:
    # /_next/static/<BUILD_ID>/_buildManifest.js
    m = re.search(r"/_next/static/([^/]+)/_buildManifest\.js", html)
    return m.group(1) if m else None


def _walk_strings(obj: Any):
    if isinstance(obj, dict):
        for _, v in obj.items():
            yield from _walk_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_strings(v)
    elif isinstance(obj, str):
        yield obj


def _pick_latest_year_from_titles(strings: List[str], must_contain: str) -> Optional[int]:
    years: List[int] = []
    must = must_contain.lower()
    for s in strings:
        s_low = s.lower()
        if must in s_low:
            # grab any year in the string
            for y in re.findall(r"\b(19\d{2}|20\d{2})\b", s):
                yy = int(y)
                if 1990 <= yy <= 2099:
                    years.append(yy)
    return max(years) if years else None


def lookup_icc_state_adoption(state_abbr: str, debug_ui: bool = False) -> CodeAdoptionResult:
    abbr = (state_abbr or "").strip().upper()
    if abbr not in STATE_ABBR_TO_NAME:
        raise ValueError(f"Unknown state abbreviation: {abbr}")

    state_name = STATE_ABBR_TO_NAME[abbr]
    slug = _slugify_state_name(state_name)
    state_url = STATE_PAGE_TEMPLATE.format(slug=slug)

    html = _http_get(state_url)
    build_id = _extract_build_id(html)

    if debug_ui:
        with st.expander("🔎 ICC debug (HTML + build id)"):
            st.write("State URL:", state_url)
            st.write("HTML length:", len(html))
            st.write("Build ID:", build_id if build_id else "❌ not found")
            # show only a small prefix
            st.code(html[:1200])

    if not build_id:
        raise ValueError("Could not extract Next.js build id from ICC HTML (site structure may have changed).")

    data_url = NEXT_DATA_TEMPLATE.format(build_id=build_id, slug=slug)
    data = _http_get_json(data_url)

    if debug_ui:
        with st.expander("🔎 ICC debug (JSON keys preview)"):
            st.write("Next data URL:", data_url)
            st.write("Top keys:", list(data.keys()))
            st.code(json.dumps(list(data.keys()), indent=2)[:800])

    strings = list(_walk_strings(data))

    # Titles on the ICC page contain "(IBC)" and "(IECC)" in many states
    ibc_year = _pick_latest_year_from_titles(strings, "International Building Code")
    iecc_year = _pick_latest_year_from_titles(strings, "International Energy Conservation Code")

    return CodeAdoptionResult(
        state_abbr=abbr,
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

    state_choice = st.selectbox("State", options=state_labels, index=default_index)
    state_abbr = state_choice.split("–")[0].strip()

    ibc_year = None
    iecc_year = None
    source_url = None

    try:
        res = lookup_icc_state_adoption(state_abbr, debug_ui=True)  # set False once stable
        ibc_year = res.ibc_year
        iecc_year = res.iecc_year
        source_url = res.state_url

        st.success("ICC state adoption found.")
        st.caption(f"Source: {source_url}")

    except Exception as e:
        st.warning("ICC lookup failed — enter years manually.")
        with st.expander("Show lookup error"):
            st.code(str(e))

    c1, c2 = st.columns(2)
    with c1:
        st.metric("IBC (State)", str(ibc_year) if ibc_year else "Not found")
    with c2:
        st.metric("IECC (State)", str(iecc_year) if iecc_year else "Not found")

    # Manual override
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
    }
