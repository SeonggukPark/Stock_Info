from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import load_config, load_env_file
from .emailer import send_report_email
from .market_calendar import is_us_trading_day
from .render import print_html_to_pdf, write_html_report, write_text_report
from .report_builder import collect_us_report


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    env_path = Path(args.env)
    load_env_file(env_path)
    config = load_config(config_path)

    tz = ZoneInfo(config.report.timezone)
    generated_at = datetime.now(tz)
    report_date = date.fromisoformat(args.date) if args.date else generated_at.date()

    if not args.force and not is_us_trading_day(report_date):
        print(f"{report_date.isoformat()} is not a US trading day. Use --force to generate anyway.")
        return 0

    sample_data = args.sample_data
    if args.live:
        sample_data = False

    report = collect_us_report(config, report_date, generated_at, sample_data=sample_data)
    output_dir = config.report.output_dir / report_date.isoformat()
    html_path = write_html_report(report, output_dir)
    text_path = write_text_report(report, output_dir)
    pdf_path, pdf_warning = print_html_to_pdf(html_path, output_dir / "us_report.pdf")

    if pdf_warning:
        print(pdf_warning)

    print(f"HTML: {html_path}")
    print(f"TEXT: {text_path}")
    if pdf_path:
        print(f"PDF:  {pdf_path}")

    should_send = args.send and not args.dry_run
    if should_send:
        subject = f"{config.email.subject_prefix} {report.title}"
        attachments = [path for path in [pdf_path, html_path] if path]
        send_report_email(
            config.email,
            subject=subject,
            html_body=html_path.read_text(encoding="utf-8"),
            text_body=text_path.read_text(encoding="utf-8"),
            attachments=attachments,
        )
        print("Email sent.")
    else:
        print("Dry-run complete. Add --send to email the report.")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and optionally email the daily US stock report.")
    parser.add_argument("--config", default="config/us_report.toml", help="Path to TOML config.")
    parser.add_argument("--env", default=".env", help="Path to .env file.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD. Defaults to today in the report timezone.")
    parser.add_argument("--dry-run", action="store_true", help="Generate files without sending email.")
    parser.add_argument("--send", action="store_true", help="Send the generated report by email.")
    parser.add_argument("--sample-data", action="store_true", help="Force built-in sample data.")
    parser.add_argument("--live", action="store_true", help="Force live providers. If keys are missing, sections may be empty.")
    parser.add_argument("--force", action="store_true", help="Generate even on non-trading days.")
    return parser


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
