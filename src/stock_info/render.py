from __future__ import annotations

import html
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from string import Template

from .models import EventItem, MacroPoint, NewsItem, Quote, ReportData
from .report_builder import format_pct


def write_html_report(report: ReportData, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    template = Template((Path(__file__).parent / "templates" / "us_report.html").read_text(encoding="utf-8"))
    html_text = template.safe_substitute(
        title=esc(report.title),
        subtitle=esc(report.subtitle),
        generated_at=esc(report.generated_at.strftime("%Y-%m-%d %H:%M %Z")),
        headline=esc(report.headline),
        summary=esc(report.summary),
        sample_banner=_sample_banner(report),
        warning_block=_warning_block(report.warnings),
        market_rows=_quote_rows(report.market_snapshot),
        movers_up_rows=_quote_rows(report.movers_up, include_note=True),
        movers_down_rows=_quote_rows(report.movers_down, include_note=True),
        watchlist_rows=_quote_rows(report.watchlist),
        macro_cards=_macro_cards(report.macro_points),
        news_items=_news_items(report.news),
        event_rows=_event_rows(report.events),
        reference_links=_reference_links(report.references),
    )
    path = output_dir / "us_report.html"
    path.write_text(html_text, encoding="utf-8")
    return path


def write_text_report(report: ReportData, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        report.title,
        report.subtitle,
        "",
        report.headline,
        report.summary,
        "",
        "[Market Snapshot]",
        *[_quote_text(q) for q in report.market_snapshot],
        "",
        "[News]",
        *[f"- {item.title} ({item.source}) {item.url}" for item in report.news],
        "",
        "[Warnings]",
        *[f"- {warning}" for warning in report.warnings],
    ]
    path = output_dir / "us_report.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def print_html_to_pdf(html_path: Path, pdf_path: Path) -> tuple[Path | None, str | None]:
    browser = _find_browser()
    if not browser:
        return None, "Edge/Chrome 실행 파일을 찾지 못해 PDF 생성을 건너뛰었습니다."

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stock-info-browser-") as temp_dir:
        command = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={temp_dir}",
            f"--print-to-pdf={pdf_path.resolve()}",
            html_path.resolve().as_uri(),
        ]
        result = subprocess.run(command, capture_output=True, timeout=60, check=False)
    if result.returncode != 0 or not pdf_path.exists():
        output = result.stderr or result.stdout
        message = output.decode("utf-8", errors="replace").strip() if output else "unknown browser print error"
        return None, f"PDF 생성 실패: {message}"
    return pdf_path, None


def _find_browser() -> str | None:
    env_path = os.getenv("BROWSER_PATH", "").strip()
    if env_path and Path(env_path).exists():
        return env_path

    candidates = [
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("chromium"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def _sample_banner(report: ReportData) -> str:
    if not report.is_sample:
        return ""
    return '<div class="banner">샘플 데이터 리포트입니다. 실제 운용 전 API 키를 연결하세요.</div>'


def _warning_block(warnings: list[str]) -> str:
    if not warnings:
        return ""
    items = "".join(f"<li>{esc(item)}</li>" for item in warnings)
    return f'<section class="section warning"><h2>운영 알림</h2><ul>{items}</ul></section>'


def _quote_rows(quotes: list[Quote], include_note: bool = False) -> str:
    if not quotes:
        colspan = 6 if include_note else 5
        return f'<tr><td colspan="{colspan}" class="empty">데이터 없음</td></tr>'
    rows = []
    for quote in quotes:
        pct = quote.change_pct or 0
        tone = "positive" if pct > 0 else "negative" if pct < 0 else "neutral"
        note = f"<td>{esc(quote.note)}</td>" if include_note else ""
        rows.append(
            "<tr>"
            f"<td><strong>{esc(quote.symbol)}</strong><span>{esc(quote.name)}</span></td>"
            f"<td>{format_price(quote.price)}</td>"
            f'<td class="{tone}">{format_change(quote.change)}</td>'
            f'<td class="{tone}">{format_pct(quote.change_pct)}</td>'
            f"<td>{format_volume(quote.volume)}</td>"
            f"{note}"
            f"<td>{esc(quote.source)}</td>"
            "</tr>"
        )
    return "".join(rows)


def _macro_cards(points: list[MacroPoint]) -> str:
    if not points:
        return '<div class="empty">데이터 없음</div>'
    return "".join(
        f'<div class="metric"><span>{esc(point.label)}</span><strong>{esc(point.value)}</strong><em>{esc(point.note or point.source)}</em></div>'
        for point in points
    )


def _news_items(news: list[NewsItem]) -> str:
    if not news:
        return '<li class="empty">데이터 없음</li>'
    return "".join(
        f'<li><a href="{esc(item.url)}">{esc(item.title)}</a><span>{esc(item.source)}</span><p>{esc(item.summary)}</p></li>'
        for item in news
    )


def _event_rows(events: list[EventItem]) -> str:
    if not events:
        return '<tr><td colspan="4" class="empty">데이터 없음</td></tr>'
    return "".join(
        "<tr>"
        f"<td>{esc(item.time)}</td>"
        f"<td>{esc(item.title)}</td>"
        f"<td>{esc(', '.join(item.symbols))}</td>"
        f"<td>{esc(item.source)}</td>"
        "</tr>"
        for item in events
    )


def _reference_links(references: dict[str, str]) -> str:
    if not references:
        return ""
    return "".join(f'<a href="{esc(url)}">{esc(name)}</a>' for name, url in references.items())


def _quote_text(quote: Quote) -> str:
    return f"- {quote.symbol}: {format_price(quote.price)} ({format_pct(quote.change_pct)})"


def format_price(value: float | None) -> str:
    if value is None:
        return "-"
    return f"${value:,.2f}"


def format_change(value: float | None) -> str:
    if value is None:
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:,.2f}"


def format_volume(value: int | None) -> str:
    if value is None:
        return "-"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)
