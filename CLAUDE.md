# tidepool: notes for agents

Tests: `python3 -m unittest discover -s tests -t .` (stdlib only; fixtures in `tests/fixtures/` are real NOAA predictions for December 2026).

## Tests must check the behaviour asked for, not just how many

When a task says *where* or *which* things appear ("only on each day's first row", "once per station", "in time order"), the test must assert exactly which items are set. A count is not enough.

- Work out the expected positions from the fixture, e.g. the index of the first tide of each date, then `assertEqual` the set or list of non-empty positions with them.
- Check the test against a plausible wrong version: the value on the last row instead of the first, or two on one day and none on another. If the test still passes, tighten it.
- Checking counts or totals is fine on top of that, but never on its own.
