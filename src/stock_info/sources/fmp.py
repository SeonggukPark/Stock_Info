from __future__ import annotations

from urllib.error import HTTPError

from datetime import date

from ..models import EventItem, NewsItem, Quote
from .http import HttpJsonClient


class FmpClient:
    base_url = "https://financialmodelingprep.com/stable"

    def __init__(self, api_key: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.http = HttpJsonClient(timeout_seconds)

    def quotes(self, symbols: list[str]) -> list[Quote]:
        if not symbols:
            return []
        joined = ",".join(symbols)
        payload = self._get_json_with_legacy_fallback(
            f"{self.base_url}/batch-quote",
            {"symbols": joined, "apikey": self.api_key},
            f"https://financialmodelingprep.com/api/v3/quote/{joined}",
            {"apikey": self.api_key},
        )
        quotes: list[Quote] = []
        for item in payload if isinstance(payload, list) else []:
            quotes.append(
                Quote(
                    symbol=str(item.get("symbol", "")).upper(),
                    name=str(item.get("name") or item.get("symbol") or ""),
                    price=_float(item.get("price")),
                    change=_float(item.get("change")),
                    change_pct=_float(item.get("changesPercentage")),
                    volume=_int(item.get("volume")),
                    source="FMP",
                )
            )
        return quotes

    def stock_news(self, symbols: list[str], limit: int = 8) -> list[NewsItem]:
        payload = self._get_json_with_legacy_fallback(
            f"{self.base_url}/news/stock",
            {"symbols": ",".join(symbols[:8]), "limit": limit, "apikey": self.api_key},
            "https://financialmodelingprep.com/api/v3/stock_news",
            {"tickers": ",".join(symbols[:8]), "limit": limit, "apikey": self.api_key},
        )
        news: list[NewsItem] = []
        for item in payload if isinstance(payload, list) else []:
            title = str(item.get("title") or "").strip()
            url = str(item.get("url") or "").strip()
            if not title or not url:
                continue
            news.append(
                NewsItem(
                    title=title,
                    source=str(item.get("publisher") or item.get("site") or "FMP"),
                    url=url,
                    summary=str(item.get("text") or item.get("summary") or "")[:280],
                )
            )
        return news

    def earnings_calendar(self, day: date, limit: int = 10) -> list[EventItem]:
        payload = self._get_json_with_legacy_fallback(
            f"{self.base_url}/earnings-calendar",
            {"from": day.isoformat(), "to": day.isoformat(), "apikey": self.api_key},
            "https://financialmodelingprep.com/api/v3/earning_calendar",
            {"from": day.isoformat(), "to": day.isoformat(), "apikey": self.api_key},
        )
        events: list[EventItem] = []
        for item in (payload if isinstance(payload, list) else [])[:limit]:
            symbol = str(item.get("symbol") or "").upper()
            eps = item.get("eps")
            revenue = item.get("revenue")
            detail = []
            if eps not in (None, ""):
                detail.append(f"EPS {eps}")
            if revenue not in (None, ""):
                detail.append(f"Revenue {revenue}")
            suffix = f" ({', '.join(detail)})" if detail else ""
            events.append(EventItem("Earnings", f"{symbol} 실적 발표{suffix}", "FMP", [symbol] if symbol else []))
        return events

    def _get_json_with_legacy_fallback(
        self,
        stable_url: str,
        stable_params: dict[str, str | int | float | None],
        legacy_url: str,
        legacy_params: dict[str, str | int | float | None],
    ) -> object:
        try:
            return self.http.get_json(stable_url, stable_params)
        except HTTPError as exc:
            if exc.code not in {402, 403, 404}:
                raise
            return self.http.get_json(legacy_url, legacy_params)


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
