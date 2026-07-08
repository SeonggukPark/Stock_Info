from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReportSettings:
    market: str
    timezone: str
    send_time: str
    title_prefix: str
    output_dir: Path
    fallback_to_sample_when_no_keys: bool


@dataclass(frozen=True)
class EmailSettings:
    smtp_host: str
    smtp_port: int
    smtp_user_env: str
    smtp_password_env: str
    mail_to_env: str
    from_name: str
    subject_prefix: str


@dataclass(frozen=True)
class SourceSettings:
    enabled: list[str]
    fmp_api_key_env: str
    finnhub_api_key_env: str
    alphavantage_api_key_env: str
    fred_api_key_env: str
    request_timeout_seconds: int


@dataclass(frozen=True)
class AppConfig:
    report: ReportSettings
    email: EmailSettings
    watchlist: list[str]
    market_snapshot_symbols: list[str]
    sources: SourceSettings
    references: dict[str, str]


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config(path: Path) -> AppConfig:
    with path.open("rb") as fp:
        data = tomllib.load(fp)

    report_data = data["report"]
    email_data = data["email"]
    sources_data = data["sources"]

    return AppConfig(
        report=ReportSettings(
            market=str(report_data.get("market", "US")),
            timezone=str(report_data.get("timezone", "Asia/Seoul")),
            send_time=str(report_data.get("send_time", "21:00")),
            title_prefix=str(report_data.get("title_prefix", "미국주식 데일리 리포트")),
            output_dir=Path(str(report_data.get("output_dir", "output/reports/us"))),
            fallback_to_sample_when_no_keys=bool(report_data.get("fallback_to_sample_when_no_keys", True)),
        ),
        email=EmailSettings(
            smtp_host=str(email_data.get("smtp_host", "smtp.gmail.com")),
            smtp_port=int(email_data.get("smtp_port", 587)),
            smtp_user_env=str(email_data.get("smtp_user_env", "SMTP_USER")),
            smtp_password_env=str(email_data.get("smtp_password_env", "SMTP_APP_PASSWORD")),
            mail_to_env=str(email_data.get("mail_to_env", "MAIL_TO")),
            from_name=str(email_data.get("from_name", "Stock Info Bot")),
            subject_prefix=str(email_data.get("subject_prefix", "[US Stocks]")),
        ),
        watchlist=[str(symbol).upper() for symbol in data.get("watchlist", {}).get("symbols", [])],
        market_snapshot_symbols=[str(symbol).upper() for symbol in data.get("market", {}).get("snapshot_symbols", [])],
        sources=SourceSettings(
            enabled=[str(name) for name in sources_data.get("enabled", [])],
            fmp_api_key_env=str(sources_data.get("fmp_api_key_env", "FMP_API_KEY")),
            finnhub_api_key_env=str(sources_data.get("finnhub_api_key_env", "FINNHUB_API_KEY")),
            alphavantage_api_key_env=str(sources_data.get("alphavantage_api_key_env", "ALPHAVANTAGE_API_KEY")),
            fred_api_key_env=str(sources_data.get("fred_api_key_env", "FRED_API_KEY")),
            request_timeout_seconds=int(sources_data.get("request_timeout_seconds", 12)),
        ),
        references={str(k).replace("_", " "): str(v) for k, v in data.get("references", {}).items()},
    )
