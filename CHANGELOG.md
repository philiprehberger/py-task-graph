# Changelog

## 0.3.0 (2026-04-27)

- Add `pass_results` parameter to `run()` and `run_parallel()` — when True, each task receives its declared dependencies' return values as keyword arguments
- Backfill missing dates on historical CHANGELOG entries

## 0.2.1 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility

## 0.2.0 (2026-03-27)

- Add per-task `timeout` parameter to `@graph.task()` and `add_task()` using `concurrent.futures` timeout
- Add per-task `retries` parameter for automatic retry on failure
- Store timeout/retries as metadata on registered tasks
- Add `.github/` issue templates, PR template, and Dependabot config
- Update README with full badge set and Support section

## 0.1.8 (2026-03-22)

- Add test suite for task graph operations

## 0.1.7 (2026-03-19)

- Standardize README structure and fix compliance issues

## 0.1.6 (2026-03-17)

- Fix classifiers and URLs, add badges, convert API to table format

## 0.1.5 (2026-03-15)

- Add pytest and mypy tool configuration to pyproject.toml

## 0.1.4 (2026-03-13)

- Fix version tag alignment with PyPI

## 0.1.2 (2026-03-11)

- Add Development section to README

## 0.1.0 (2026-03-10)

- Initial release
- Decorator-based task registration
- Topological sort with cycle detection
- Sequential and parallel execution
- Dry run mode
