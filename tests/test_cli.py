import io
import json
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

from tidepool.cli import main
from tidepool.tides import load, tidepool_windows

FIXTURES = Path(__file__).parent / "fixtures"
SF = str(FIXTURES / "hilo-9414290.json")


def run(*argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = main(list(argv))
    return code, out.getvalue()


class JsonOutputTest(unittest.TestCase):
    def test_json_parses_with_iso_times(self):
        code, out = run(SF, "--now", "2026-12-01T00:00", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["next_high"]["time"], "2026-12-01T05:45:00")
        self.assertEqual(data["next_high"]["kind"], "H")
        self.assertIsInstance(data["next_high"]["height_ft"], float)
        low = data["next_low"]
        self.assertEqual(low["kind"], "L")
        self.assertGreater(datetime.fromisoformat(low["time"]), datetime(2026, 12, 1))

    def test_json_windows_match_tidepool_windows(self):
        _, out = run(SF, "--now", "2026-12-01T00:00", "--json")
        windows = json.loads(out)["windows"]
        expected = tidepool_windows(load(SF))
        self.assertEqual(len(windows), len(expected))
        self.assertGreater(len(windows), 0)
        for got, want in zip(windows, expected):
            self.assertEqual(datetime.fromisoformat(got["start"]), want.start)
            self.assertEqual(datetime.fromisoformat(got["end"]), want.end)
            self.assertEqual(datetime.fromisoformat(got["low"]["time"]), want.low.when)
            self.assertEqual(got["low"]["height_ft"], want.low.height_ft)

    def test_json_with_no_tides_left_gives_nulls(self):
        _, out = run(SF, "--now", "2027-01-01T00:00", "--json")
        data = json.loads(out)
        self.assertIsNone(data["next_high"])
        self.assertIsNone(data["next_low"])

    def test_json_stdout_stays_parseable_with_html(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            _, out = run(SF, "--now", "2026-12-01T00:00", "--json", "--html", str(Path(d) / "sf.html"))
            self.assertTrue((Path(d) / "sf.html").exists())
        json.loads(out)

    def test_text_output_unchanged_without_flag(self):
        _, out = run(SF, "--now", "2026-12-01T00:00")
        self.assertIn("Next high: Tue 01 Dec 05:45", out)


if __name__ == "__main__":
    unittest.main()
