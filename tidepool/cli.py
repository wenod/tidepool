"""`python -m tidepool PREDICTIONS.json [--station NAME] [--html OUT] [--units {imperial,metric}]`"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .render import UNITS, dashboard, when
from .tides import load, next_tide, tidepool_windows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tidepool", description="Tides from a NOAA predictions file.")
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--station", default="the station")
    parser.add_argument("--now", type=datetime.fromisoformat, default=None, help="pretend it's this time")
    parser.add_argument("--html", type=Path, help="write the dashboard here")
    parser.add_argument("--units", choices=UNITS, default="imperial", help="heights in feet (imperial) or meters (metric)")
    args = parser.parse_args(argv)

    tides = load(args.predictions)
    now = args.now or datetime.now()
    high, low = next_tide(tides, now, "H"), next_tide(tides, now, "L")
    print(f"Next high: {when(high, args.units)}")
    print(f"Next low:  {when(low, args.units)}")
    print(f"Tidepool windows this month: {len(tidepool_windows(tides))}")
    if args.html:
        args.html.write_text(dashboard(args.station, tides, now, args.units))
        print(f"Wrote {args.html}")
    return 0
