from __future__ import annotations

import re

from ..models import Quote
from .http import HttpJsonClient


PLAIN_EQUITY_SYMBOL = re.compile(r"^[A-Z]{1,5}(?:[.-][A-Z])?$")


class AlphaVantageClient:
    base_url = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.http = HttpJsonClient(timeout_seconds)

    def top_gainers_losers(self) -> tuple[list[Quote], list[Quote]]:
        payload = self.http.get_json(self.base_url, {"function": "TOP_GAINERS_LOSERS", "apikey": self.api_key})
        return (
            self._parse_movers(payload.get("top_gainers", []) if isinstance(payload, dict) else [], "Alpha Vantage"),
            self._parse_movers(payload.get("top_losers", []) if isinstance(payload, dict) else [], "Alpha Vantage"),
        )

    @staticmethod
    def _parse_movers(items: list[dict[str, object]], source: str) -> list[Quote]:
        quotes: list[Quote] = []
        for item in items:
            symbol = str(item.get("ticker") or "").upper()
            if not _is_plain_equity_symbol(symbol):
                continue
            quotes.append(
                Quote(
                    symbol=symbol,
                    name=symbol,
                    price=_float(item.get("price")),
                    change=None,
                    change_pct=_pct(item.get("change_percentage")),
                    volume=_int(item.get("volume")),
                    source=source,
                )
            )
            if len(quotes) >= 8:
                break
        return quotes


def _pct(value: object) -> float | None:
    if value is None:
        return None
    return _float(str(value).replace("%", ""))


def _is_plain_equity_symbol(symbol: str) -> bool:
    if not PLAIN_EQUITY_SYMBOL.fullmatch(symbol):
        return False
    if "+" in symbol or "^" in symbol or "/" in symbol:
        return False
    # Alpha Vantage gainers/losers often include warrants, rights, and units.
    if len(symbol) >= 5 and symbol.endswith(("W", "WS", "WT", "R", "U")):
        return False
    return True


def _float(value: object) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _int(value: object) -> int | None:
    try:
        return int(float(value)) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None
