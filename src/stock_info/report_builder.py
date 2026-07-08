from __future__ import annotations

import os
from datetime import date, datetime, timedelta

from .config import AppConfig
from .models import EventItem, MacroPoint, NewsItem, Quote, ReportData
from .sources.alpha_vantage import AlphaVantageClient
from .sources.finnhub import FinnhubClient
from .sources.fmp import FmpClient
from .sources.fred import FredClient
from .sources.sample import build_sample_report


SYMBOL_NAMES = {
    "SPY": "S&P 500 ETF",
    "QQQ": "Nasdaq 100 ETF",
    "DIA": "Dow 30 ETF",
    "IWM": "Russell 2000 ETF",
    "VIXY": "VIX Futures ETF",
    "NVDA": "NVIDIA",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
    "GOOGL": "Alphabet",
    "TSLA": "Tesla",
    "AVGO": "Broadcom",
    "AMD": "Advanced Micro Devices",
    "PLTR": "Palantir",
}


def collect_us_report(config: AppConfig, report_date: date, generated_at: datetime, sample_data: bool) -> ReportData:
    if sample_data:
        return build_sample_report(report_date, generated_at, config.report.title_prefix, config.references)

    keys = {
        "fmp": os.getenv(config.sources.fmp_api_key_env, "").strip(),
        "finnhub": os.getenv(config.sources.finnhub_api_key_env, "").strip(),
        "alpha_vantage": os.getenv(config.sources.alphavantage_api_key_env, "").strip(),
        "fred": os.getenv(config.sources.fred_api_key_env, "").strip(),
    }
    has_any_key = any(keys.values())
    if not has_any_key and config.report.fallback_to_sample_when_no_keys:
        report = build_sample_report(report_date, generated_at, config.report.title_prefix, config.references)
        return _with_warning(report, "API 키가 없어 샘플 데이터로 리포트를 생성했습니다.")

    warnings: list[str] = []
    market_snapshot: list[Quote] = []
    watchlist: list[Quote] = []
    movers_up: list[Quote] = []
    movers_down: list[Quote] = []
    alpha_movers_up: list[Quote] = []
    alpha_movers_down: list[Quote] = []
    news: list[NewsItem] = []
    events: list[EventItem] = []
    macro_points: list[MacroPoint] = []

    if "fmp" in config.sources.enabled and keys["fmp"]:
        try:
            fmp = FmpClient(keys["fmp"], config.sources.request_timeout_seconds)
            market_snapshot = fmp.quotes(config.market_snapshot_symbols)
            watchlist = fmp.quotes(config.watchlist)
            news.extend(fmp.stock_news(config.watchlist, limit=8))
            events.extend(fmp.earnings_calendar(report_date, limit=10))
        except Exception as exc:  # noqa: BLE001
            warnings.append(_provider_error("FMP", exc))

    if "alpha_vantage" in config.sources.enabled and keys["alpha_vantage"]:
        try:
            alpha = AlphaVantageClient(keys["alpha_vantage"], config.sources.request_timeout_seconds)
            alpha_movers_up, alpha_movers_down = alpha.top_gainers_losers()
        except Exception as exc:  # noqa: BLE001
            warnings.append(_provider_error("Alpha Vantage", exc))

    if "finnhub" in config.sources.enabled and keys["finnhub"]:
        try:
            finnhub = FinnhubClient(keys["finnhub"], config.sources.request_timeout_seconds)
            if not market_snapshot:
                market_snapshot = finnhub.quotes(config.market_snapshot_symbols, SYMBOL_NAMES)
            if not watchlist:
                watchlist = finnhub.quotes(config.watchlist, SYMBOL_NAMES)
            if len(news) < 5:
                news.extend(_dedupe_news(finnhub.market_news(limit=8), news))
                if len(news) < 5 and config.watchlist:
                    start = report_date - timedelta(days=3)
                    for item in finnhub.company_news(config.watchlist[0], start, report_date, limit=3):
                        if item.url not in {existing.url for existing in news}:
                            news.append(item)
        except Exception as exc:  # noqa: BLE001
            warnings.append(_provider_error("Finnhub", exc))

    if "fred" in config.sources.enabled and keys["fred"]:
        try:
            macro_points.extend(FredClient(keys["fred"], config.sources.request_timeout_seconds).macro_points())
        except Exception as exc:  # noqa: BLE001
            warnings.append(_provider_error("FRED", exc))

    watchlist_up = sorted([q for q in watchlist if (q.change_pct or 0) > 0], key=lambda q: q.change_pct or 0, reverse=True)
    watchlist_down = sorted([q for q in watchlist if (q.change_pct or 0) < 0], key=lambda q: q.change_pct or 0)
    movers_up = watchlist_up[:5] if watchlist_up else alpha_movers_up
    movers_down = watchlist_down[:5] if watchlist_down else alpha_movers_down

    if has_any_key and not any([market_snapshot, watchlist, movers_up, movers_down, news, events, macro_points]):
        report = build_sample_report(report_date, generated_at, config.report.title_prefix, config.references)
        return _with_warning(report, "라이브 데이터 수집에 실패해 샘플 데이터로 대체했습니다.")

    sample_report = build_sample_report(report_date, generated_at, config.report.title_prefix, config.references)
    if not market_snapshot:
        market_snapshot = sample_report.market_snapshot
        warnings.append("시장 스냅샷은 라이브 데이터 수집 실패로 샘플 데이터로 대체했습니다.")
    if not watchlist:
        watchlist = sample_report.watchlist
        warnings.append("관심 종목 시세는 라이브 데이터 수집 실패로 샘플 데이터로 대체했습니다.")
    if not movers_up:
        movers_up = sample_report.movers_up
        warnings.append("상승 종목은 라이브 데이터 수집 실패로 샘플 데이터로 대체했습니다.")
    if not movers_down:
        movers_down = sample_report.movers_down
        warnings.append("하락 종목은 라이브 데이터 수집 실패로 샘플 데이터로 대체했습니다.")
    if not events:
        events = sample_report.events
        warnings.append("일정 데이터는 라이브 데이터 수집 실패로 샘플 데이터로 대체했습니다.")

    title = f"{report_date.month}월 {report_date.day}일 {config.report.title_prefix}"
    headline = _make_headline(news, movers_up, movers_down)
    summary = _make_summary(market_snapshot, movers_up, movers_down, macro_points)

    if not news:
        warnings.append("뉴스 데이터가 비어 있습니다.")

    return ReportData(
        report_date=report_date,
        generated_at=generated_at,
        title=title,
        subtitle="미국주식 자동 리포트",
        headline=headline,
        summary=summary,
        is_sample=False,
        market_snapshot=market_snapshot,
        movers_up=movers_up[:8],
        movers_down=movers_down[:8],
        watchlist=watchlist,
        macro_points=macro_points,
        news=news[:8],
        events=events[:10],
        references=config.references,
        warnings=warnings,
    )


def _with_warning(report: ReportData, warning: str) -> ReportData:
    return ReportData(
        report_date=report.report_date,
        generated_at=report.generated_at,
        title=report.title,
        subtitle=report.subtitle,
        headline=report.headline,
        summary=report.summary,
        is_sample=report.is_sample,
        market_snapshot=report.market_snapshot,
        movers_up=report.movers_up,
        movers_down=report.movers_down,
        watchlist=report.watchlist,
        macro_points=report.macro_points,
        news=report.news,
        events=report.events,
        references=report.references,
        warnings=[warning, *report.warnings],
    )


def _dedupe_news(incoming: list[NewsItem], existing: list[NewsItem]) -> list[NewsItem]:
    urls = {item.url for item in existing}
    result = []
    for item in incoming:
        if item.url not in urls:
            result.append(item)
            urls.add(item.url)
    return result


def _provider_error(provider: str, exc: Exception) -> str:
    message = str(exc)
    if "403" in message or "Forbidden" in message:
        return (
            f"{provider} 데이터 수집 실패: 403 Forbidden. "
            "API 키, 구독 플랜 권한, 일일 호출 한도, 엔드포인트 접근 권한을 확인하세요."
        )
    return f"{provider} 데이터 수집 실패: {message}"


def _make_headline(news: list[NewsItem], movers_up: list[Quote], movers_down: list[Quote]) -> str:
    if news:
        return news[0].title
    if movers_up:
        top = movers_up[0]
        return f"{top.symbol} 강세, 변동률 {format_pct(top.change_pct)}"
    if movers_down:
        top = movers_down[0]
        return f"{top.symbol} 약세, 변동률 {format_pct(top.change_pct)}"
    return "미국주식 주요 변수 점검"


def _make_summary(
    market_snapshot: list[Quote],
    movers_up: list[Quote],
    movers_down: list[Quote],
    macro_points: list[MacroPoint],
) -> str:
    parts: list[str] = []
    if market_snapshot:
        positive = [q for q in market_snapshot if (q.change_pct or 0) >= 0]
        parts.append(f"시장 스냅샷 {len(market_snapshot)}개 중 {len(positive)}개가 플러스권입니다.")
    if movers_up:
        parts.append(f"상승 모멘텀은 {movers_up[0].symbol}이 가장 두드러집니다.")
    if movers_down:
        parts.append(f"하락 압력은 {movers_down[0].symbol}을 우선 확인합니다.")
    if macro_points:
        parts.append(f"매크로 지표는 {macro_points[0].label}부터 점검합니다.")
    return " ".join(parts) if parts else "라이브 데이터가 제한적입니다. 출처 링크와 함께 추가 확인이 필요합니다."


def format_pct(value: float | None) -> str:
    if value is None:
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"
