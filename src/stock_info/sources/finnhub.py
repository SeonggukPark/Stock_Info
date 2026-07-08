from __future__ import annotations

from datetime import date

from ..models import NewsItem, Quote
from .http import HttpJsonClient


class FinnhubClient:
    base_url = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.http = HttpJsonClient(timeout_seconds)

    def market_news(self, limit: int = 8) -> list[NewsItem]:
        payload = self.http.get_json(f"{self.base_url}/news", {"category": "general", "token": self.api_key})
        news: list[NewsItem] = []
        for item in payload if isinstance(payload, list) else []:
            title = str(item.get("headline") or "").strip()
            url = str(item.get("url") or "").strip()
            if not title or not url:
                continue
            news.append(
                NewsItem(
                    title=title,
                    source=str(item.get("source") or "Finnhub"),
                    url=url,
                    summary=str(item.get("summary") or "")[:280],
                )
            )
            if len(news) >= limit:
                break
        return news

    def quotes(self, symbols: list[str], name_map: dict[str, str] | None = None) -> list[Quote]:
        quotes: list[Quote] = []
        for symbol in symbols:
            quote = self.quote(symbol, name_map or {})
            if quote:
                quotes.append(quote)
        return quotes

    def quote(self, symbol: str, name_map: dict[str, str]) -> Quote | None:
        normalized = symbol.upper()
        payload = self.http.get_json(f"{self.base_url}/quote", {"symbol": normalized, "token": self.api_key})
        if not isinstance(payload, dict):
            return None
        price = _float(payload.get("c"))
        previous_close = _float(payload.get("pc"))
        if price is None or price == 0:
            return None
        change = _float(payload.get("d"))
        change_pct = _float(payload.get("dp"))
        if change is None and previous_close not in (None, 0):
            change = price - previous_close
        if change_pct is None and previous_close not in (None, 0):
            change_pct = ((price - previous_close) / previous_close) * 100
        return Quote(
            symbol=normalized,
            name=name_map.get(normalized, normalized),
            price=price,
            change=change,
            change_pct=change_pct,
            volume=None,
            source="Finnhub",
        )

    def company_news(self, symbol: str, from_day: date, to_day: date, limit: int = 3) -> list[NewsItem]:
        payload = self.http.get_json(
            f"{self.base_url}/company-news",
            {
                "symbol": symbol,
                "from": from_day.isoformat(),
                "to": to_day.isoformat(),
                "token": self.api_key,
            },
        )
        news: list[NewsItem] = []
        for item in payload if isinstance(payload, list) else []:
            title = str(item.get("headline") or "").strip()
            url = str(item.get("url") or "").strip()
            if title and url:
                news.append(NewsItem(title, str(item.get("source") or "Finnhub"), url, str(item.get("summary") or "")[:280]))
            if len(news) >= limit:
                break
        return news


def _float(value: object) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None
