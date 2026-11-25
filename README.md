# tidepool

Tides from NOAA's predictions: the next high and low, each day's range, and the minus tides worth a trip to the tidepools.

```bash
python3 -m tidepool tests/fixtures/hilo-9414290.json --station-id 9414290 --html out/sf.html
```

`--station-id` looks up the name and state in `tests/fixtures/stations.json` (or `--stations FILE`); `--station NAME` sets the name by hand and wins if both are given.

Fixtures are real December 2026 predictions from NOAA CO-OPS for San Francisco (9414290), The Battery (8518750) and Seattle (9447130).

Tests: `python3 -m unittest discover -s tests -t .`
