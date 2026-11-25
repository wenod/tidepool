"""The dashboard: one HTML page for a station's month of tides."""
from __future__ import annotations

from datetime import datetime
from html import escape

from .tides import Tide, daily_range, next_tide, tidepool_windows

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<style>
body {{ font: 15px/1.5 system-ui, sans-serif; margin: 2rem auto; max-width: 52rem; padding: 0 1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ padding: .25rem .5rem; border-bottom: 1px solid #ddd; text-align: left; }}
.low {{ color: #1d5fa8; }}
</style></head><body>
<h1>{title}</h1>
<p>Next high: {next_high}. Next low: {next_low}.</p>
<h2>Tidepool windows</h2>
<ul>{windows}</ul>
<h2>Tides</h2>
<table><tr><th>When</th><th>Height ({unit})</th><th></th><th>Day's range</th></tr>{rows}</table>
</body></html>
"""


UNITS = ("imperial", "metric")
METERS_PER_FOOT = 0.3048


def unit_label(units: str = "imperial") -> str:
    return "m" if units == "metric" else "ft"


def height(feet: float, units: str = "imperial", ft_decimals: int = 1) -> str:
    """A height given in feet as a number in `units`: meters always to 2 decimals."""
    if units == "metric":
        return f"{feet * METERS_PER_FOOT:.2f}"
    return f"{feet:.{ft_decimals}f}"


def when(tide: Tide | None, units: str = "imperial") -> str:
    """"Tue 01 Dec 05:45 (5.4 ft)", or "none"."""
    if not tide:
        return "none"
    return tide.when.strftime("%a %d %b %H:%M") + f" ({height(tide.height_ft, units)} {unit_label(units)})"


def _range(tides: list[Tide], t: Tide, units: str) -> str:
    r = daily_range(tides, t.when.date())
    if not r:
        return ""
    return height(r, units) if units == "metric" else str(r)


def dashboard(station: str, tides: list[Tide], now: datetime, units: str = "imperial") -> str:
    unit = unit_label(units)
    rows = "".join(
        f'<tr class="{"low" if t.is_low else "high"}"><td>{t.when:%a %d %b %H:%M}</td>'
        f"<td>{height(t.height_ft, units, 2)}</td><td>{'Low' if t.is_low else 'High'}</td>"
        f"<td>{_range(tides, t, units)}</td></tr>"
        for t in tides
    )
    windows = "".join(
        f"<li>{w.start:%a %d %b %H:%M}–{w.end:%H:%M}, low {height(w.low.height_ft, units)} {unit}</li>"
        for w in tidepool_windows(tides)
    ) or "<li>No minus tides this month.</li>"
    return PAGE.format(
        title=escape(f"Tides at {station}"),
        next_high=escape(when(next_tide(tides, now, "H"), units)),
        next_low=escape(when(next_tide(tides, now, "L"), units)),
        windows=windows,
        rows=rows,
        unit=unit,
    )
