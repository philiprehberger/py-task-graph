# philiprehberger-task-graph

[![Tests](https://github.com/philiprehberger/py-task-graph/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-task-graph/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-task-graph.svg)](https://pypi.org/project/philiprehberger-task-graph/)
[![GitHub release](https://img.shields.io/github/v/release/philiprehberger/py-task-graph)](https://github.com/philiprehberger/py-task-graph/releases)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-task-graph)](https://github.com/philiprehberger/py-task-graph/commits/main)
[![License](https://img.shields.io/github/license/philiprehberger/py-task-graph)](LICENSE)
[![Bug Reports](https://img.shields.io/github/issues/philiprehberger/py-task-graph/bug)](https://github.com/philiprehberger/py-task-graph/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![Feature Requests](https://img.shields.io/github/issues/philiprehberger/py-task-graph/enhancement)](https://github.com/philiprehberger/py-task-graph/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Lightweight task dependency engine with topological execution.

## Installation

```bash
pip install philiprehberger-task-graph
```

## Usage

```python
from philiprehberger_task_graph import TaskGraph

graph = TaskGraph()

@graph.task()
def fetch_data():
    return download()

@graph.task(depends=["fetch_data"])
def process_data():
    return transform()

@graph.task(depends=["process_data"])
def save_results():
    return store()

# Run tasks in dependency order
results = graph.run()

# Or run with parallelism
results = graph.run_parallel(max_workers=4)
```

### Programmatic API

```python
graph = TaskGraph()
graph.add_task("fetch", fetch_fn)
graph.add_task("process", process_fn, depends=["fetch"])
graph.add_task("save", save_fn, depends=["process"])

# Preview execution order
order = graph.dry_run()
# ["fetch", "process", "save"]
```

### Timeout

Set a maximum execution time for a task. Raises `TimeoutError` if the task exceeds the limit.

```python
@graph.task(timeout=30.0)
def slow_task():
    return long_running_operation()

# Or with add_task
graph.add_task("fetch", fetch_fn, timeout=10.0)
```

### Retries

Automatically retry a task on failure. The task is retried up to N times before the exception propagates.

```python
@graph.task(retries=3)
def flaky_task():
    return call_unreliable_api()

# Or with add_task
graph.add_task("fetch", fetch_fn, retries=2)
```

### Timeout and Retries Combined

```python
@graph.task(timeout=5.0, retries=2)
def resilient_task():
    return fetch_with_deadline()
```

### Cycle Detection

```python
from philiprehberger_task_graph import CycleError

# Raises CycleError if dependencies form a cycle
graph.run()
```

## API

| Function / Class | Description |
|------------------|-------------|
| `TaskGraph()` | Create a new task graph |
| `@graph.task(name=None, depends=None, timeout=None, retries=0)` | Decorator to register a task with optional timeout and retries |
| `graph.add_task(name, fn, depends=None, timeout=None, retries=0)` | Add a task programmatically |
| `graph.run()` | Execute tasks in topological order |
| `graph.run_parallel(max_workers=None)` | Execute with thread parallelism |
| `graph.dry_run()` | Return execution order without running |
| `CycleError` | Raised when a dependency cycle is detected |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this package useful, consider giving it a star on GitHub — it helps motivate continued maintenance and development.

[![LinkedIn](https://img.shields.io/badge/Philip%20Rehberger-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/in/philiprehberger)
[![More packages](https://img.shields.io/badge/more-open%20source%20packages-blue)](https://philiprehberger.com/open-source-packages)

## License

[MIT](LICENSE)
