"""Station names from a stations file: a JSON list of {"id", "name", "state", ...}."""
from __future__ import annotations

import json
from pathlib import Path

# Until there's a real stations file, the fixtures' list is the one we ship with.
DEFAULT_STATIONS = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "stations.json"


def station_label(station_id: str, path: Path = DEFAULT_STATIONS) -> str:
    """'San Francisco, CA' for '9414290'. KeyError if the id isn't in the file."""
    for station in json.loads(Path(path).read_text()):
        if str(station.get("id")) == station_id:
            return f"{station['name']}, {station['state']}" if station.get("state") else station["name"]
    raise KeyError(station_id)
