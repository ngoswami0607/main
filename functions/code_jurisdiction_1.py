from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup
import streamlit as st


ICC_US_CODES_URL = "https://codes.iccsafe.org/codes/united-states"

STATE_ABBR_TO_NAME: Dict[str, str] = {
    "WI": "Wisconsin",
    "IL": "Illinois",
    "CA": "California",
    "TX": "Texas",
    # add more as needed
}


@dataclass
class CodeAdoptionResult:
    state_name: str
    state_url: str
    ibc_year: Optional[int]
    iecc_year: Optional[int]


# ------------------------
# LOW-LEVEL HELPERS
# ------------------------
def _http_get(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text


def _normalize_state(state: str) -> str:
    s = state.strip().upper()
    return STATE_ABBR_TO_NAME.get(s, state.title())


def _extract_year(text: str, code_name: str) -> Optional[int]:
    matches = re.findall(rf"{code_name}.*?(20\d{{2}})", text, re.IGNORECASE)
    return int(matches[-1]) if matches else None


def lookup_icc_state_adoption(state: str) -> CodeAdoptionResult:
    state_name = _normalize_state(state)

    html = _http_get(ICC_US_CODES_URL)
    soup = BeautifulSoup(html, "html.parser")

    state_url = None
    for a in soup.find_all("a", href=True):
        if a.text.strip() == state_name:
            state_url = "https://codes.iccsafe.org" + a["href"]
            break

    if not state_url:
        raise ValueError(f"State not found on ICC site: {state_name}")

    state_html = _http_get(state_url)

    return CodeAdoptionResult(
        state_name=state_name,
        state_url=state_url,
        ibc_year=_extract_year(state_html, "International Building Code"),
        iecc_year=_extract_year(state_html, "International Energy Conservation Code"),
    )
