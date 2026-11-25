# tidepool

Tides from NOAA's predictions: the next high and low, each day's range, and the minus tides worth a trip to the tidepools.

```bash
python3 -m tidepool tests/fixtures/hilo-9414290.json --station "San Francisco" --html out/sf.html
```

Add `--units metric` to show heights in meters (to 2 decimals) in the output and the dashboard; heights are kept in feet internally.

Fixtures are real December 2026 predictions from NOAA CO-OPS for San Francisco (9414290), The Battery (8518750) and Seattle (9447130).

Tests: `python3 -m unittest discover -s tests -t .`
