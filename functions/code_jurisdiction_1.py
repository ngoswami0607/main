from __future__ import annotations

import os
from typing import Optional

try:
    import streamlit as st  # Preferred for Streamlit Cloud and @st.cache_resource
except Exception:  # If not running under Streamlit
    st = None  # type: ignore

from openai import OpenAI

def _read_openai_api_key() -> Optional[str]:
    """
    Read the OpenAI API key, preferring Streamlit Secrets if available,
    otherwise falling back to the environment variable.
    """
    # Streamlit Secrets (Streamlit Cloud)
    if st is not None and hasattr(st, "secrets"):
        try:
            key = st.secrets.get("OPENAI_API_KEY")
            if key:
                return key
        except Exception:
            # Secrets not configured or not accessible; fall back to env var
            pass

    # Environment variable (local dev or other hosts)
    return os.environ.get("OPENAI_API_KEY")

# Build the OpenAI client, cached appropriately for the runtime
if st is not None:
    # In Streamlit, cache the resource per session to avoid re-instantiation
    @st.cache_resource(show_spinner=False)
    def _build_openai_client() -> OpenAI:
        api_key = _read_openai_api_key()
        if not api_key:
            raise RuntimeError(
                "Missing OPENAI_API_KEY. Add it in Streamlit Secrets (Cloud) or your environment (local)."
            )
        return OpenAI(api_key=api_key)
else:
    # Outside Streamlit, keep a simple module-level singleton
    _CLIENT_SINGLETON: Optional[OpenAI] = None

    def _build_openai_client() -> OpenAI:
        global _CLIENT_SINGLETON
        if _CLIENT_SINGLETON is None:
            api_key = _read_openai_api_key()
            if not api_key:
                raise RuntimeError(
                    "Missing OPENAI_API_KEY. Set it as an environment variable."
                )
            _CLIENT_SINGLETON = OpenAI(api_key=api_key)
        return _CLIENT_SINGLETON

def get_openai_client() -> OpenAI:
    """
    Explicit getter for the OpenAI client (preferred in new code).
    Example:
        client = get_openai_client()
        resp = client.responses.create(model="gpt-4o-mini", input="Hello")
    """
    return _build_openai_client()

class _LazyClient:
    """
    Proxy that lazily builds and then forwards attributes to the real OpenAI client.
    This lets existing code keep using `client.*` without modification.
    """

    __slots__ = ("_client",)

    def __init__(self):
        self._client: Optional[OpenAI] = None

    def _ensure(self) -> None:
        if self._client is None:
            self._client = _build_openai_client()

    def __getattr__(self, name):
        self._ensure()
        return getattr(self._client, name)

# Export a lazy `client` so existing calls keep working:
client = _LazyClient()
