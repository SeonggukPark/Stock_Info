from __future__ import annotations

from ..models import MacroPoint
from .http import HttpJsonClient


class FredClient:
    base_url = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.http = HttpJsonClient(timeout_seconds)

    def macro_points(self) -> list[MacroPoint]:
        series = {
            "DGS10": "미 10년물 금리",
            "DGS2": "미 2년물 금리",
            "DFF": "연방기금 실효금리",
        }
        points: list[MacroPoint] = []
        for series_id, label in series.items():
            value = self._latest_value(series_id)
            if value:
                points.append(MacroPoint(label, f"{value}%", "FRED", series_id))
        return points

    def _latest_value(self, series_id: str) -> str | None:
        payload = self.http.get_json(
            self.base_url,
            {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 10,
            },
        )
        observations = payload.get("observations", []) if isinstance(payload, dict) else []
        for item in observations:
            value = str(item.get("value") or "")
            if value and value != ".":
                return value
        return None
