"""Tide events and what to do with them: the next high and low, a day's range, low-tide windows."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


@dataclass(frozen=True)
class Tide:
    """One predicted high or low water."""

    when: datetime
    height_ft: float
    kind: str  # "H" or "L"

    @property
    def is_low(self) -> bool:
        return self.kind == "L"


def parse_predictions(raw: dict) -> list[Tide]:
    """Tides from a NOAA CO-OPS `predictions` response (interval=hilo), oldest first."""
    tides = [
        Tide(datetime.strptime(p["t"], "%Y-%m-%d %H:%M"), float(p["v"]), p["type"])
        for p in raw.get("predictions", [])
    ]
    return sorted(tides, key=lambda t: t.when)


def load(path: str | Path) -> list[Tide]:
    return parse_predictions(json.loads(Path(path).read_text()))


def next_tide(tides: list[Tide], after: datetime, kind: str | None = None) -> Tide | None:
    """The first tide after `after`, of `kind` ("H" or "L") when given."""
    for tide in tides:
        if tide.when > after and (kind is None or tide.kind == kind):
            return tide
    return None


def on_day(tides: list[Tide], day: date) -> list[Tide]:
    return [t for t in tides if t.when.date() == day]


def daily_range(tides: list[Tide], day: date) -> float | None:
    """Highest high minus lowest low on `day`, in feet."""
    todays = on_day(tides, day)
    highs = [t.height_ft for t in todays if t.kind == "H"]
    lows = [t.height_ft for t in todays if t.kind == "L"]
    if not highs or not lows:
        return None
    return round(max(highs) - min(lows), 3)


@dataclass(frozen=True)
class Window:
    """A low tide good for tidepooling: around `low`, from `start` to `end`."""

    low: Tide
    start: datetime
    end: datetime


def tidepool_windows(tides: list[Tide], below_ft: float = 0.0, margin: timedelta = timedelta(hours=1)) -> list[Window]:
    """Low tides at or below `below_ft`, each with an hour either side."""
    return [Window(t, t.when - margin, t.when + margin) for t in tides if t.is_low and t.height_ft <= below_ft]
