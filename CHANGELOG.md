# Changelog

## 0.2.0 (2026-03-27)

- Add per-task `timeout` parameter to `@graph.task()` and `add_task()` using `concurrent.futures` timeout
- Add per-task `retries` parameter for automatic retry on failure
- Store timeout/retries as metadata on registered tasks
- Add `.github/` issue templates, PR template, and Dependabot config
- Update README with full badge set and Support section

## 0.1.8 (2026-03-22)

- Add test suite for task graph operations

## 0.1.7

- Standardize README structure and fix compliance issues

## 0.1.6

- Fix classifiers and URLs, add badges, convert API to table format

## 0.1.5

- Add pytest and mypy tool configuration to pyproject.toml

## 0.1.4

- Fix version tag alignment with PyPI

## 0.1.2

- Add Development section to README

## 0.1.0 (2026-03-10)

- Initial release
- Decorator-based task registration
- Topological sort with cycle detection
- Sequential and parallel execution
- Dry run mode
