from datetime import date
import unittest

from stock_info.market_calendar import is_us_trading_day


class MarketCalendarTests(unittest.TestCase):
    def test_weekday_trading_day(self) -> None:
        self.assertTrue(is_us_trading_day(date(2026, 7, 8)))

    def test_observed_independence_day(self) -> None:
        self.assertFalse(is_us_trading_day(date(2026, 7, 3)))

    def test_weekend(self) -> None:
        self.assertFalse(is_us_trading_day(date(2026, 7, 4)))


if __name__ == "__main__":
    unittest.main()
