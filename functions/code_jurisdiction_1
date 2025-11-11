from __future__ import annotations
import os
from typing import Optional

try:
    import streamlit as st
except Exception:
    st = None  # type: ignore

from openai import OpenAI

# --- Helper: read API key ---
def _read_openai_api_key() -> Optional[str]:
    """Read OpenAI API key from Streamlit secrets or environment."""
    if st is not None and hasattr(st, "secrets"):
        try:
            key = st.secrets.get("OPENAI_API_KEY")
            if key:
                return key
        except Exception:
            pass
    return os.environ.get("OPENAI_API_KEY")

# --- Helper: build OpenAI client ---
if st is not None:
    @st.cache_resource(show_spinner=False)
    def _build_openai_client() -> OpenAI:
        api_key = _read_openai_api_key()
        if not api_key:
            raise RuntimeError(
                "Missing OPENAI_API_KEY. Add it in Streamlit Secrets (Cloud) or your environment (local)."
            )
        return OpenAI(api_key=api_key)
else:
    _CLIENT_SINGLETON: Optional[OpenAI] = None

    def _build_openai_client() -> OpenAI:
        global _CLIENT_SINGLETON
        if _CLIENT_SINGLETON is None:
            api_key = _read_openai_api_key()
            if not api_key:
                raise RuntimeError("Missing OPENAI_API_KEY. Set it as an environment variable.")
            _CLIENT_SINGLETON = OpenAI(api_key=api_key)
        return _CLIENT_SINGLETON

def get_openai_client() -> OpenAI:
    """Return an initialized OpenAI client."""
    return _build_openai_client()

class _LazyClient:
    """Lazy proxy that initializes the OpenAI client only when used."""
    __slots__ = ("_client",)

    def __init__(self):
        self._client: Optional[OpenAI] = None

    def _ensure(self):
        if self._client is None:
            self._client = _build_openai_client()

    def __getattr__(self, name):
        self._ensure()
        return getattr(self._client, name)

client = _LazyClient()

# --- Streamlit functional block ---
def code_jurisdiction_1():
    """
    Step in the Wind Load Calculator: determine jurisdiction and code reference.
    Lets user input location, and optionally uses OpenAI to infer governing code version.
    """
    if st is None:
        raise RuntimeError("Streamlit is required to run this function.")

    st.subheader("🏛️ Code Jurisdiction / Project Location")

    location = st.text_input("Enter the project location (City, State):", "")

    ai_enabled = _read_openai_api_key() is not None
    jurisdiction = ""

    if location:
        if ai_enabled:
            with st.spinner("Determining applicable code jurisdiction..."):
                try:
                    client = get_openai_client()
                    prompt = (
                        f"The project is located in {location}. "
                        "Based on U.S. code adoption trends, identify the most likely "
                        "applicable building code and ASCE 7 wind load reference version "
                        "(e.g., IBC 2021 with ASCE 7-16). "
                        "Respond concisely."
                    )

                    response = client.responses.create(
                        model="gpt-4o-mini",
                        input=prompt,
                    )
                    jurisdiction = response.output_text.strip()
                    st.success(f"Most likely code jurisdiction: **{jurisdiction}**")

                except Exception as e:
                    st.warning(
                        f"OpenAI lookup failed ({e}). Please enter code manually below."
                    )
                    ai_enabled = False
        else:
            st.info("No OpenAI key detected — please enter jurisdiction manually.")

    if not ai_enabled:
        jurisdiction = st.text_input(
            "Enter code jurisdiction manually (e.g., IBC 2021 / ASCE 7-16):", jurisdiction
        )

    return jurisdiction or location
