# Agent Guidance

## Working Style

- Inspect `git status` and relevant files before editing. Treat existing and uncommitted changes as user work; do not overwrite or discard them.
- Keep changes within the requested scope. Do not use destructive cleanup or reset commands, and do not remove build artifacts unless asked.
- For substantial or ambiguous work, summarize the proposed approach and confirm important assumptions before implementation. Keep progress updates concise and report test/build results clearly.
- Do not delegate work unless explicitly requested.
- Do not publish packages or change the version unless the user asks.

## Project Layout

- Python package: `src/kalshi_csv/`
- CLI: `src/kalshi_csv/cli.py`
- CSV parsing and performance calculations: `src/kalshi_csv/parser.py`
- Legacy and modern web servers/renderers: `src/kalshi_csv/web.py`
- Modern dashboard template and local assets: `src/kalshi_csv/templates/` and `src/kalshi_csv/static/`
- Theme definitions: `src/kalshi_csv/themes.json`
- Tests: `tests/`

Keep the version in `pyproject.toml` and `src/kalshi_csv/__init__.py` synchronized. The package supports Python 3.8+, but the current Makefile reads `pyproject.toml` with `tomllib`, so its default workflow requires Python 3.11+; the project `.venv` is the preferred development environment.

## Domain Rules

- S&P 500 contract tiers are based on entry price and must remain disjoint:
  - Entry `<= $0.40`
  - Entry `> $0.40` and `<= $0.70`
  - Entry `> $0.70` and `<= $0.85`
  - Entry `> $0.85`
- Tier win rate is positive-P&L trades divided by all trades in the tier. Pushes count in the denominator but not in average win/loss calculations.
- Average wins and losses are arithmetic means of per-trade P&L including fees. Total net P&L includes all trades and fees. Display an average as `N/A` when that tier has no wins or no losses.
- Test price boundaries explicitly, especially exactly `$0.40`, `$0.70`, and `$0.85`. Prefer synthetic test data over the private transaction CSV.

## Web UI and Themes

- Keep `--legacy-web` and `--modern-web` as separate, mutually exclusive modes; preserve the legacy HTML 4.01 behavior.
- Both web servers intentionally bind to `0.0.0.0` by default. Do not change the host binding without the user's direction.
- The modern dashboard includes the full parsed trade history. Preserve safe JSON embedding and render CSV-controlled strings as text, not executable HTML.
- Alpine.js is vendored under `static/` with its MIT license. Do not introduce CDN scripts, remote fonts, or other external runtime assets; the dashboard should work offline.
- Preserve all 40 supplied palettes and their eight normal and eight bright ANSI colors. CSS semantic colors should use the theme variables; `--negative` is derived from ANSI red (`ansi-1`), including the `side-no` badge.
- When adding packaged templates or assets, update the Hatch build configuration and verify they are present in the wheel.

## Tests and Builds

- Use `make test` for source tests; it sets `PYTHONPATH=src` and uses `.venv/bin/python` by default.
- `make build` builds the wheel and source distribution.
- `make install` builds and force-reinstalls the version-matched wheel into the configured Python environment.
- Plain `make` / `make all` runs tests, builds and installs the wheel, then verifies the installed version and dashboard assets. It changes `dist/` and the selected Python environment; use it when that full build/install cycle is intended, not for test-only checks.
- `make PYTHON=python3` overrides the interpreter. Do not publish the resulting distributions unless explicitly asked.
- Update `README.md` when changing user-facing CLI options, build commands, or dashboard behavior.
