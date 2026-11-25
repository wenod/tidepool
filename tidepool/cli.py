"""`python -m tidepool PREDICTIONS.json [--station NAME | --station-id ID] [--html OUT] [--units {imperial,metric}] [--below FEET]`"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .render import UNITS, dashboard, when
from .stations import DEFAULT_STATIONS, station_label
from .tides import load, next_tide, tidepool_windows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tidepool", description="Tides from a NOAA predictions file.")
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--station", help="station name for the dashboard (wins over --station-id)")
    parser.add_argument("--station-id", help="NOAA station id, e.g. 9414290; name and state come from --stations")
    parser.add_argument("--stations", type=Path, default=DEFAULT_STATIONS, help="stations JSON file")
    parser.add_argument("--now", type=datetime.fromisoformat, default=None, help="pretend it's this time")
    parser.add_argument("--html", type=Path, help="write the dashboard here")
    parser.add_argument("--units", choices=UNITS, default="imperial", help="heights in feet (imperial) or meters (metric)")
    parser.add_argument("--below", type=float, default=0.0, metavar="FEET",
                        help="count low tides at or below this height in feet as tidepool windows (default 0.0)")
    args = parser.parse_args(argv)

    station = args.station
    if station is None and args.station_id:
        try:
            station = station_label(args.station_id, args.stations)
        except KeyError:
            parser.error(f"unknown station id {args.station_id} (not in {args.stations})")
        except OSError as e:
            parser.error(f"can't read stations file {args.stations}: {e.strerror}")
    station = station or "the station"

    tides = load(args.predictions)
    now = args.now or datetime.now()
    high, low = next_tide(tides, now, "H"), next_tide(tides, now, "L")
    print(f"Next high: {when(high, args.units)}")
    print(f"Next low:  {when(low, args.units)}")
    print(f"Tidepool windows this month: {len(tidepool_windows(tides, args.below))}")
    if args.html:
        args.html.write_text(dashboard(station, tides, now, args.units, below_ft=args.below))
        print(f"Wrote {args.html}")
    return 0
