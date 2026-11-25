"""`python -m tidepool PREDICTIONS.json [--station NAME] [--html OUT] [--json]`"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .render import dashboard
from .tides import Tide, Window, load, next_tide, tidepool_windows


def tide_json(tide: Tide | None) -> dict | None:
    if tide is None:
        return None
    return {"time": tide.when.isoformat(), "height_ft": tide.height_ft, "kind": tide.kind}


def window_json(window: Window) -> dict:
    return {"low": tide_json(window.low), "start": window.start.isoformat(), "end": window.end.isoformat()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tidepool", description="Tides from a NOAA predictions file.")
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--station", default="the station")
    parser.add_argument("--now", type=datetime.fromisoformat, default=None, help="pretend it's this time")
    parser.add_argument("--html", type=Path, help="write the dashboard here")
    parser.add_argument("--json", action="store_true", help="print the next high, next low and windows as JSON")
    args = parser.parse_args(argv)

    tides = load(args.predictions)
    now = args.now or datetime.now()
    high, low = next_tide(tides, now, "H"), next_tide(tides, now, "L")
    windows = tidepool_windows(tides)
    if args.json:
        print(json.dumps({
            "station": args.station,
            "now": now.isoformat(),
            "next_high": tide_json(high),
            "next_low": tide_json(low),
            "windows": [window_json(w) for w in windows],
        }, indent=2))
    else:
        print(f"Next high: {high.when:%a %d %b %H:%M} ({high.height_ft:.1f} ft)" if high else "Next high: none")
        print(f"Next low:  {low.when:%a %d %b %H:%M} ({low.height_ft:.1f} ft)" if low else "Next low: none")
        print(f"Tidepool windows this month: {len(windows)}")
    if args.html:
        args.html.write_text(dashboard(args.station, tides, now))
        print(f"Wrote {args.html}", file=sys.stderr if args.json else sys.stdout)
    return 0
