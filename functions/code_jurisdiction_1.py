from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

import requests
from bs4 import BeautifulSoup


ICC_US_CODES_URL = "https://codes.iccsafe.org/codes/united-states"

STATE_ABBR_TO_NAME: Dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin",
    "WY": "Wyoming",
}


@dataclass
class CodeAdoptionResult:
    state_name: str
    state_url: str
    ibc_year: Optional[int]
    iecc_year: Optional[int]


def _http_get(url: str, timeout_s: int = 15) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WindLoadCalculator/1.0)",
        "Accept": "text/html,application/xhtml+xml",
    }
    resp = requests.get(url, headers=headers, timeout=timeout_s)
    resp.raise_for_status()
    return resp.text


def _normalize_state(state_input: str) -> str:
    s = (state_input or "").strip()
    if not s:
        raise ValueError("State is required (name or 2-letter abbreviation).")

    s_up = s.upper()
    if len(s_up) == 2 and s_up in STATE_ABBR_TO_NAME:
        return STATE_ABBR_TO_NAME[s_up]

    # Title-case normalization for common cases
    return s.title()


def _build_state_link_map(us_codes_html: str) -> Dict[str, str]:
    """
    Parses the ICC US codes landing page and builds:
    { "Wisconsin": "https://codes.iccsafe.org/codes/wisconsin", ... }
    """
    soup = BeautifulSoup(us_codes_html, "html.parser")
    links = {}

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = (a.get_text() or "").strip()

        # ICC uses absolute/relative links; we normalize to absolute
        if href.startswith("/codes/") and text:
            abs_url = "https://codes.iccsafe.org" + href
            # Many links exist; we only want state names likely on the page
            # Example text: "Wisconsin"
            if re.fullmatch(r"[A-Za-z .'-]{3,}", text):
                links[text.title()] = abs_url

    return links


def _extract_code_year(page_text: str, code_name: str) -> Optional[int]:
    """
    Try to find a 4-digit year near the code name.
    Works best when the page contains strings like:
    "International Building Code (2021)" or "International Energy Conservation Code 2018"
    """
    # windowed search: find code name occurrences and scan nearby text for a year
    candidates = []
    for m in re.finditer(re.escape(code_name), page_text, flags=re.IGNORECASE):
        start = max(0, m.start() - 120)
        end = min(len(page_text), m.end() + 120)
        snippet = page_text[start:end]
        years = re.findall(r"\b(19\d{2}|20\d{2})\b", snippet)
        candidates.extend([int(y) for y in years])

    # Prefer most recent plausible year
    if candidates:
        candidates = [y for y in candidates if 1990 <= y <= 2099]
        return max(candidates) if candidates else None
    return None


def lookup_icc_state_adoption(state: str) -> CodeAdoptionResult:
    """
    Given a state name or abbreviation, find the ICC state page and extract IBC/IECC years.
    """
    state_name = _normalize_state(state)

    us_html = _http_get(ICC_US_CODES_URL)
    state_links = _build_state_link_map(us_html)

    if state_name not in state_links:
        # fallback: try loose match
        matches = [k for k in state_links.keys() if k.lower() == state_name.lower()]
        if matches:
            state_name = matches[0]
        else:
            raise ValueError(f"Could not find '{state_name}' on ICC US codes page.")

    state_url = state_links[state_name]
    state_html = _http_get(state_url)

    # Extract years (best-effort)
    ibc_year = _extract_code_year(state_html, "International Building Code")
    iecc_year = _extract_code_year(state_html, "International Energy Conservation Code")

    return CodeAdoptionResult(
        state_name=state_name,
        state_url=state_url,
        ibc_year=ibc_year,
        iecc_year=iecc_year,
    )

