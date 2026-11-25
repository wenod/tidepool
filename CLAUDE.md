# tidepool: notes for agents

Tests: `python3 -m unittest discover -s tests -t .` (stdlib only; fixtures in `tests/fixtures/` are real NOAA predictions for December 2026).

## Tests must check the behaviour asked for, not just how many

When a task says *where* or *which* things appear ("only on each day's first row", "once per station", "in time order"), the test must assert exactly which items are set. A count is not enough.

- Work out the expected positions from the fixture, e.g. the index of the first tide of each date, then `assertEqual` the set or list of non-empty positions with them.
- Check the test against a plausible wrong version: the value on the last row instead of the first, or two on one day and none on another. If the test still passes, tighten it.
- Checking counts or totals is fine on top of that, but never on its own.

## Files the user passes in can be bad, and each kind of bad gets its own error

The fixtures are well formed, but the files users pass in (`--stations`, predictions) won't always be. For any file the CLI reads, every failure must end in a `parser.error` that names the real problem. None may end in a traceback.

- Missing or unreadable file: `OSError`.
- Malformed JSON: `json.JSONDecodeError` (a `ValueError`). Catch it wherever you catch `OSError`.
- Entry found but missing a required field (e.g. a station with no `"name"`): say which field is missing. Don't let it raise the same exception you use for "not found". A `KeyError` from `entry["name"]` must not end up as "unknown id". Validate the field, or raise a dedicated exception for lookups.
- Add a test for each case, using a small temp file. Assert the exit and the message text, so a wrong message fails the test.
