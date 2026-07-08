import unittest

from stock_info.sources.alpha_vantage import AlphaVantageClient


class AlphaVantageTests(unittest.TestCase):
    def test_filters_non_common_stock_symbols(self) -> None:
        rows = [
            {"ticker": "NVNIW", "price": "1.23", "change_percentage": "20%", "volume": "1000"},
            {"ticker": "TE+", "price": "1.23", "change_percentage": "20%", "volume": "1000"},
            {"ticker": "NVDA", "price": "167.21", "change_percentage": "3.15%", "volume": "92500000"},
        ]

        parsed = AlphaVantageClient._parse_movers(rows, "test")

        self.assertEqual([quote.symbol for quote in parsed], ["NVDA"])


if __name__ == "__main__":
    unittest.main()
