import io
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
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

    def test_dashboard_shows_each_days_range_once(self):
        page = dashboard("San Francisco", self.sf, datetime(2026, 12, 1))
        rows = re.findall(r'<tr class="(?:low|high)">(.*?)</tr>', page)
        self.assertEqual(len(rows), len(self.sf))
        ranges = [re.findall(r"<td>(.*?)</td>", row)[-1] for row in rows]
        days = {t.when.date() for t in self.sf}
        self.assertEqual(len(days), 31)
        self.assertEqual(sum(1 for r in ranges if r), 31)
        for t, r in zip(self.sf, ranges):
            if r:
                self.assertEqual(r, str(daily_range(self.sf, t.when.date())))

    def test_metric_dashboard_shows_each_days_range_once_in_meters(self):
        page = dashboard("San Francisco", self.sf, datetime(2026, 12, 1), units="metric")
        rows = re.findall(r'<tr class="(?:low|high)">(.*?)</tr>', page)
        ranges = [re.findall(r"<td>(.*?)</td>", row)[-1] for row in rows]
        self.assertEqual(sum(1 for r in ranges if r), 31)
        for t, r in zip(self.sf, ranges):
            if r:
                self.assertEqual(r, f"{daily_range(self.sf, t.when.date()) * 0.3048:.2f}")

    def test_dashboard_in_feet_by_default(self):
        page = dashboard("San Francisco", self.sf, datetime(2026, 12, 1))
        self.assertIn("Next high: Tue 01 Dec 05:45 (5.4 ft)", page)
        self.assertIn("<th>Height (ft)</th>", page)
        self.assertIn("<td>5.41</td>", page)
        self.assertIn("<td>4.771</td>", page)
        self.assertIn("low -0.2 ft", page)

    def test_dashboard_in_meters(self):
        page = dashboard("San Francisco", self.sf, datetime(2026, 12, 1), units="metric")
        self.assertIn("Next high: Tue 01 Dec 05:45 (1.65 m)", page)
        self.assertIn("Next low: Tue 01 Dec 11:37 (0.66 m)", page)
        self.assertIn("<th>Height (m)</th>", page)
        self.assertIn("<td>1.65</td>", page)
        self.assertIn("<td>1.45</td>", page)
        self.assertIn("low -0.06 m", page)
        self.assertNotIn(" ft", page)


class CliTest(unittest.TestCase):
    def run_cli(self, *extra):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([str(FIXTURES / "hilo-9414290.json"), "--now", "2026-12-01T00:00", *extra])
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_feet_by_default(self):
        out = self.run_cli()
        self.assertIn("Next high: Tue 01 Dec 05:45 (5.4 ft)", out)
        self.assertIn("Next low:  Tue 01 Dec 11:37 (2.2 ft)", out)
        self.assertEqual(out, self.run_cli("--units", "imperial"))

    def test_metric(self):
        out = self.run_cli("--units", "metric")
        self.assertIn("Next high: Tue 01 Dec 05:45 (1.65 m)", out)
        self.assertIn("Next low:  Tue 01 Dec 11:37 (0.66 m)", out)
        self.assertNotIn("ft", out)

    def test_metric_dashboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "sf.html"
            self.run_cli("--units", "metric", "--html", str(html))
            self.assertIn("(1.65 m)", html.read_text())

    def test_rejects_unknown_units(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main([str(FIXTURES / "hilo-9414290.json"), "--units", "furlongs"])

    def test_station_id_with_metric_dashboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "sf.html"
            self.run_cli("--station-id", "9414290", "--units", "metric", "--html", str(html))
            page = html.read_text()
            self.assertIn("Tides at San Francisco, CA", page)
            self.assertIn("(1.65 m)", page)


if __name__ == "__main__":
    unittest.main()
