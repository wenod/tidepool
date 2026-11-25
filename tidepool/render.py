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
<table><tr><th>When</th><th>Height (ft)</th><th></th><th>Day's range</th></tr>{rows}</table>
</body></html>
"""


def _when(tide: Tide | None) -> str:
    return tide.when.strftime("%a %d %b %H:%M") + f" ({tide.height_ft:.1f} ft)" if tide else "none"


def dashboard(station: str, tides: list[Tide], now: datetime) -> str:
    rows = "".join(
        f'<tr class="{"low" if t.is_low else "high"}"><td>{t.when:%a %d %b %H:%M}</td>'
        f"<td>{t.height_ft:.2f}</td><td>{'Low' if t.is_low else 'High'}</td>"
        f"<td>{daily_range(tides, t.when.date()) or ''}</td></tr>"
        for t in tides
    )
    windows = "".join(
        f"<li>{w.start:%a %d %b %H:%M}–{w.end:%H:%M}, low {w.low.height_ft:.1f} ft</li>" for w in tidepool_windows(tides)
    ) or "<li>No minus tides this month.</li>"
    return PAGE.format(
        title=escape(f"Tides at {station}"),
        next_high=escape(_when(next_tide(tides, now, "H"))),
        next_low=escape(_when(next_tide(tides, now, "L"))),
        windows=windows,
        rows=rows,
    )
