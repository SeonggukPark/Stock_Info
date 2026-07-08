from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass(frozen=True)
class Quote:
    symbol: str
    name: str
    price: float | None
    change: float | None
    change_pct: float | None
    volume: int | None
    source: str
    note: str = ""


@dataclass(frozen=True)
class NewsItem:
    title: str
    source: str
    url: str
    summary: str = ""


@dataclass(frozen=True)
class EventItem:
    time: str
    title: str
    source: str
    symbols: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MacroPoint:
    label: str
    value: str
    source: str
    note: str = ""


@dataclass(frozen=True)
class ReportData:
    report_date: date
    generated_at: datetime
    title: str
    subtitle: str
    headline: str
    summary: str
    is_sample: bool
    market_snapshot: list[Quote]
    movers_up: list[Quote]
    movers_down: list[Quote]
    watchlist: list[Quote]
    macro_points: list[MacroPoint]
    news: list[NewsItem]
    events: list[EventItem]
    references: dict[str, str]
    warnings: list[str] = field(default_factory=list)
