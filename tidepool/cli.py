"""`python -m tidepool PREDICTIONS.json [--station NAME] [--html OUT] [--below FEET]`"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .render import dashboard
from .tides import load, next_tide, tidepool_windows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tidepool", description="Tides from a NOAA predictions file.")
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--station", default="the station")
    parser.add_argument("--now", type=datetime.fromisoformat, default=None, help="pretend it's this time")
    parser.add_argument("--html", type=Path, help="write the dashboard here")
    parser.add_argument("--below", type=float, default=0.0, metavar="FEET",
                        help="count low tides at or below this height as tidepool windows (default 0.0)")
    args = parser.parse_args(argv)

    tides = load(args.predictions)
    now = args.now or datetime.now()
    high, low = next_tide(tides, now, "H"), next_tide(tides, now, "L")
    print(f"Next high: {high.when:%a %d %b %H:%M} ({high.height_ft:.1f} ft)" if high else "Next high: none")
    print(f"Next low:  {low.when:%a %d %b %H:%M} ({low.height_ft:.1f} ft)" if low else "Next low: none")
    print(f"Tidepool windows this month: {len(tidepool_windows(tides, args.below))}")
    if args.html:
        args.html.write_text(dashboard(args.station, tides, now, below_ft=args.below))
        print(f"Wrote {args.html}")
    return 0
