import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, datetime
from pathlib import Path

from tidepool.cli import main
from tidepool.render import dashboard
from tidepool.tides import daily_range, load, next_tide, parse_predictions, tidepool_windows

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

    def test_dashboard_names_the_station(self):
        page = dashboard("San Francisco", self.sf, datetime(2026, 12, 1))
        self.assertIn("Tides at San Francisco", page)
        self.assertIn("Next high: Tue 01 Dec 05:45", page)

    def test_dashboard_uses_the_below_threshold(self):
        default = dashboard("San Francisco", self.sf, datetime(2026, 12, 1))
        higher = dashboard("San Francisco", self.sf, datetime(2026, 12, 1), below_ft=0.5)
        self.assertGreater(higher.count("<li>"), default.count("<li>"))
        self.assertEqual(higher.count("<li>"), len(tidepool_windows(self.sf, 0.5)))


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main([str(FIXTURES / "hilo-9414290.json"), "--now", "2026-12-01T00:00", *args]), 0)
        return out.getvalue()

    def windows(self, output):
        line = next(l for l in output.splitlines() if l.startswith("Tidepool windows"))
        return int(line.rsplit(":", 1)[1])

    def test_below_finds_more_windows_than_the_default(self):
        self.assertGreater(self.windows(self.run_cli("--below", "0.5")), self.windows(self.run_cli()))

    def test_below_defaults_to_minus_tides(self):
        sf = load(FIXTURES / "hilo-9414290.json")
        self.assertEqual(self.windows(self.run_cli()), len(tidepool_windows(sf)))

    def test_below_is_passed_to_the_dashboard(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "sf.html"
            self.run_cli("--below", "0.5", "--html", str(out))
            sf = load(FIXTURES / "hilo-9414290.json")
            self.assertEqual(out.read_text().count("<li>"), len(tidepool_windows(sf, 0.5)))


if __name__ == "__main__":
    unittest.main()
