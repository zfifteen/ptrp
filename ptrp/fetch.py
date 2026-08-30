"""Injectable fetch ports. Tests inject a scripted port; production uses HTTP."""

from __future__ import annotations

import urllib.error
import urllib.request

from ptrp.constants import SOURCES


class FetchError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


PUBLIC_URLS = {
    "whitehouse_remarks": "https://www.whitehouse.gov/remarks/",
    "whitehouse_actions": "https://www.whitehouse.gov/presidential-actions/",
    "app": "https://www.presidency.ucsb.edu/",
    "factbase": "https://factba.se/",
    "federal_register": "https://www.federalregister.gov/",
    "truth_social": "https://truthsocial.com/",
    "x_personal": "https://x.com/",
    "campaign": "https://www.donaldjtrump.com/",
    "books": "https://www.whitehouse.gov/",
    "interviews": "https://www.whitehouse.gov/remarks/",
    "legal": "https://www.justice.gov/",
}


class HttpFetch:
    """Production adapter. Tests must not use this (no live network)."""

    def fetch(self, source: str, job_type: str, params: dict):
        if source not in SOURCES:
            raise FetchError(f"source not configured: {source}")
        url = PUBLIC_URLS.get(source)
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "PTRP/0.5 (Fate-operated pipeline)"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp.read(4096)
        except urllib.error.URLError as exc:
            raise FetchError(f"network error fetching {source}: {exc}") from exc
        except Exception as exc:
            raise FetchError(f"parse failed talking to {source}: {exc}") from exc
        # v0: HTTP 200 with no implemented item parser → nothing in-scope.
        return []
