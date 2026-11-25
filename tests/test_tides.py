import re
import unittest
from datetime import date, datetime
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
