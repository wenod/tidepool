import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date, datetime
from pathlib import Path

from tidepool.cli import main
from tidepool.render import dashboard
from tidepool.tides import NoaaError, daily_range, load, next_tide, parse_predictions, tidepool_windows

FIXTURES = Path(__file__).parent / "fixtures"


class TidesTest(unittest.TestCase):
    def setUp(self):
        self.sf = load(FIXTURES / "hilo-9414290.json")

    def test_parses_a_month_of_highs_and_lows_in_order(self):
        self.assertEqual(len(self.sf), 120)
        self.assertEqual(self.sf, sorted(self.sf, key=lambda t: t.when))
        self.assertEqual({t.kind for t in self.sf}, {"H", "L"})

    def test_next_tide(self):
        first = next_tide(self.sf, datetime(2026, 12, 1))
        self.assertEqual((first.when, first.kind), (datetime(2026, 12, 1, 5, 45), "H"))
        low = next_tide(self.sf, datetime(2026, 12, 1), "L")
        self.assertEqual(low.kind, "L")
        self.assertIsNone(next_tide(self.sf, datetime(2027, 1, 1)))

    def test_daily_range(self):
        r = daily_range(self.sf, date(2026, 12, 1))
        self.assertGreater(r, 0)
        self.assertIsNone(daily_range(self.sf, date(2027, 1, 1)))

    def test_tidepool_windows_are_minus_tides(self):
        windows = tidepool_windows(self.sf)
        self.assertTrue(all(w.low.height_ft <= 0 for w in windows))
        self.assertTrue(all(w.start < w.low.when < w.end for w in windows))

    def test_empty_response(self):
        self.assertEqual(parse_predictions({}), [])

    def test_noaa_error_response_raises_with_its_message(self):
        with self.assertRaises(NoaaError) as caught:
            load(FIXTURES / "error-no-predictions.json")
        self.assertIn("No Predictions data was found", str(caught.exception))

    def test_cli_prints_noaa_error_and_returns_1(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = main([str(FIXTURES / "error-no-predictions.json")])
        self.assertEqual(status, 1)
        self.assertIn("No Predictions data was found", err.getvalue())
        self.assertNotIn("Next high", out.getvalue())

    def test_dashboard_names_the_station(self):
        page = dashboard("San Francisco", self.sf, datetime(2026, 12, 1))
        self.assertIn("Tides at San Francisco", page)
        self.assertIn("Next high: Tue 01 Dec 05:45", page)


if __name__ == "__main__":
    unittest.main()
