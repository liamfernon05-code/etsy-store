"""REST connectors (httpx only, no vendor SDKs) for Google, DataForSEO and LLM search APIs.

Design rules (from the API-contract research and its critique):
 * every connector is OPTIONAL: missing credentials/approval yields an UNKNOWN finding, never a crash;
 * secrets come from the environment and are never logged or written to disk;
 * API hosts are fixed, so these calls honour HTTPS_PROXY / SSL_CERT_FILE (unlike the SSRF-hardened crawler);
 * 'quota 0 / access not approved' (GBP) is detected and reported, not retried;
 * every response that may contain user-generated text (reviews, AI answers) is treated as untrusted data.
Contracts were verified from Google discovery documents, vendor SDKs and OpenAPI specs where reachable; endpoints and
field names are exercised in tests with mock transports, NOT against live services (no credentials in the build sandbox).
Run the `smoke` command with your own keys before relying on any connector.
"""

from __future__ import annotations

import os
import ssl
import time
from typing import Any

import httpx


class ConnectorError(RuntimeError):
    def __init__(self, status: int, message: str, kind: str = "error"):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.kind = kind  # "not_approved" | "auth" | "quota" | "not_found" | "error"


def _ssl() -> ssl.SSLContext | bool:
    cafile = os.environ.get("LSA_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    return ssl.create_default_context(cafile=cafile) if cafile else True


class ApiClient:
    """Thin httpx wrapper. `transport` lets tests inject httpx.MockTransport."""

    def __init__(self, transport: httpx.BaseTransport | None = None, timeout: float = 30.0, retries: int = 0):
        """retries: extra attempts on 429/5xx with exponential backoff (honours Retry-After). Default 0: calls that cost
        money (SERP APIs, LLM search) must not be retried blindly. Never retried: 400/401/403/404."""
        self._transport = transport
        self.timeout = timeout
        self.retries = retries
        self.requests_made = 0
        self.sleep = time.sleep

    def request(self, method: str, url: str, *, headers: dict | None = None, params: Any = None,
                json: Any = None, auth: tuple[str, str] | None = None) -> dict:
        kw: dict[str, Any] = {"timeout": self.timeout, "follow_redirects": False}
        if self._transport is not None:
            kw["transport"] = self._transport
        else:
            kw["verify"] = _ssl()
        for attempt in range(self.retries + 1):
            with httpx.Client(**kw) as c:
                r = c.request(method, url, headers=headers, params=params, json=json, auth=auth)
            self.requests_made += 1
            if r.status_code in (429, 500, 502, 503, 504) and attempt < self.retries:
                try:
                    wait = float(r.headers.get("retry-after", ""))
                except ValueError:
                    wait = 2.0 ** attempt
                self.sleep(min(wait, 30.0))
                continue
            break
        if r.status_code >= 400:
            raise _classify(r)
        return r.json() if r.content else {}


def _classify(r: httpx.Response) -> ConnectorError:
    try:
        err = (r.json() or {}).get("error", {})
        msg = err.get("message") if isinstance(err, dict) else str(err)
        status_txt = err.get("status", "") if isinstance(err, dict) else ""
    except ValueError:
        msg, status_txt = r.text[:200], ""
    msg = (msg or r.text[:200] or "").strip()[:300]
    low = msg.lower()
    if r.status_code == 429:
        return ConnectorError(r.status_code, msg, "quota")
    if r.status_code in (401, 403):
        return ConnectorError(r.status_code, msg or status_txt, "auth")
    if r.status_code == 404:
        return ConnectorError(r.status_code, msg, "not_found")
    return ConnectorError(r.status_code, msg)


def google_headers(extra: dict | None = None) -> dict:
    tok = os.environ.get("GOOGLE_ACCESS_TOKEN")
    if not tok:
        raise ConnectorError(401, "Set GOOGLE_ACCESS_TOKEN (see README: gcloud auth application-default login --client-id-file=... --scopes=...)", "auth")
    h = {"Authorization": f"Bearer {tok}"}
    if os.environ.get("GOOGLE_QUOTA_PROJECT"):
        h["X-Goog-User-Project"] = os.environ["GOOGLE_QUOTA_PROJECT"]
    return {**h, **(extra or {})}
