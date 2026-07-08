from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


class HttpJsonClient:
    def __init__(self, timeout_seconds: int = 12) -> None:
        self.timeout_seconds = timeout_seconds

    def get_json(self, url: str, params: dict[str, str | int | float | None] | None = None) -> Any:
        if params:
            filtered = {k: v for k, v in params.items() if v is not None}
            query = urllib.parse.urlencode(filtered)
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{query}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "StockInfoReport/0.1 (+local personal report)",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return json.loads(response.read().decode(charset))
