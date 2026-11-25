import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from tidepool.cli import main
from tidepool.stations import station_label

FIXTURES = Path(__file__).parent / "fixtures"
SF = str(FIXTURES / "hilo-9414290.json")
STATIONS = str(FIXTURES / "stations.json")


class StationLookupTest(unittest.TestCase):
    def test_label_is_name_and_state(self):
        self.assertEqual(station_label("9414290", FIXTURES / "stations.json"), "San Francisco, CA")
        self.assertEqual(station_label("8518750", FIXTURES / "stations.json"), "The Battery, NY")

    def test_unknown_id_raises(self):
        with self.assertRaises(KeyError):
            station_label("0000000", FIXTURES / "stations.json")


class CliStationTest(unittest.TestCase):
    def run_cli(self, *args):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "page.html"
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([SF, "--now", "2026-12-01T00:00", "--html", str(out), *args])
            return code, out.read_text()

    def test_station_id_names_the_dashboard(self):
        code, page = self.run_cli("--station-id", "9414290", "--stations", STATIONS)
        self.assertEqual(code, 0)
        self.assertIn("Tides at San Francisco, CA", page)

    def test_station_id_uses_bundled_stations_by_default(self):
        code, page = self.run_cli("--station-id", "9447130")
        self.assertEqual(code, 0)
        self.assertIn("Tides at Seattle, WA", page)

    def test_station_wins_over_station_id(self):
        code, page = self.run_cli("--station", "Fort Point", "--station-id", "9414290", "--stations", STATIONS)
        self.assertEqual(code, 0)
        self.assertIn("Tides at Fort Point", page)
        self.assertNotIn("San Francisco, CA", page)

    def test_unknown_station_id_exits_2_with_message(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as cm:
            main([SF, "--station-id", "0000000", "--stations", STATIONS])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("unknown station id 0000000", err.getvalue())


if __name__ == "__main__":
    unittest.main()
