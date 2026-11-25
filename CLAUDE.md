# tidepool: notes for agents

Tests: `python3 -m unittest discover -s tests -t .` (stdlib only; fixtures in `tests/fixtures/` are real NOAA predictions for December 2026).

## Tests must check the behaviour asked for, not just how many

When a task says *where* or *which* things appear ("only on each day's first row", "once per station", "in time order"), the test must assert exactly which items are set. A count is not enough.

- Work out the expected positions from the fixture, e.g. the index of the first tide of each date, then `assertEqual` the set or list of non-empty positions with them.
- Check the test against a plausible wrong version: the value on the last row instead of the first, or two on one day and none on another. If the test still passes, tighten it.
- Checking counts or totals is fine on top of that, but never on its own.

## Filters and thresholds: test the case where nothing matches

The dashboard falls back to a placeholder when a list is empty (e.g. the tidepool windows `<ul>` shows a single "No ..." `<li>`). So counting `<li>` or `<tr>` tags can't tell "one match" from "no matches".

- When you add or change a filter, threshold or option that can leave a list empty, add a test with a value the fixture never reaches (e.g. a threshold far below the month's lowest tide), and `assertIn` the exact fallback text, including any value it interpolates.
- To check the non-empty case, pull the rendered items out by their content (a regex for the time and height), then compare them with what the function returns for that input (`tidepool_windows(...)` with the same threshold). Don't compare a tag count with `len(...)`.
- If you change the fallback wording, update the test that asserts it. A fallback nothing asserts is untested.

## Files the user passes in can be bad, and each kind of bad gets its own error

The fixtures are well formed, but the files users pass in (`--stations`, predictions) won't always be. For any file the CLI reads, every failure must end in a `parser.error` that names the real problem. None may end in a traceback.

- Missing or unreadable file: `OSError`.
- Malformed JSON: `json.JSONDecodeError` (a `ValueError`). Catch it wherever you catch `OSError`.
- Entry found but missing a required field (e.g. a station with no `"name"`): say which field is missing. Don't let it raise the same exception you use for "not found". A `KeyError` from `entry["name"]` must not end up as "unknown id". Validate the field, or raise a dedicated exception for lookups.
- Add a test for each case, using a small temp file. Assert the exit and the message text, so a wrong message fails the test.
