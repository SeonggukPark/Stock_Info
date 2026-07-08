from datetime import date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from zoneinfo import ZoneInfo
import unittest

from stock_info.render import write_html_report, write_text_report
from stock_info.sources.sample import build_sample_report


class RenderTests(unittest.TestCase):
    def test_sample_report_renders_html_and_text(self) -> None:
        report = build_sample_report(
            date(2026, 7, 8),
            datetime(2026, 7, 8, 21, 0, tzinfo=ZoneInfo("Asia/Seoul")),
            "미국주식 데일리 리포트",
            {"Yahoo Finance": "https://finance.yahoo.com/"},
        )
        with TemporaryDirectory() as temp_dir:
            html_path = write_html_report(report, Path(temp_dir))
            text_path = write_text_report(report, Path(temp_dir))
            html = html_path.read_text(encoding="utf-8")
            text = text_path.read_text(encoding="utf-8")
        self.assertIn("미국주식 데일리 리포트", html)
        self.assertNotIn("$market_rows", html)
        self.assertIn("[Market Snapshot]", text)


if __name__ == "__main__":
    unittest.main()
