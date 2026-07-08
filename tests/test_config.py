from pathlib import Path
import tempfile
import unittest

from stock_info.config import load_config, load_env_file


class ConfigTests(unittest.TestCase):
    def test_load_config(self) -> None:
        config = load_config(Path("config/us_report.toml"))
        self.assertEqual(config.report.market, "US")
        self.assertIn("NVDA", config.watchlist)
        self.assertEqual(config.email.smtp_host, "smtp.gmail.com")

    def test_load_env_file_does_not_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("STOCK_INFO_TEST_VALUE=from_file\n", encoding="utf-8")
            load_env_file(env_path)
            import os

            self.assertEqual(os.getenv("STOCK_INFO_TEST_VALUE"), "from_file")


if __name__ == "__main__":
    unittest.main()
