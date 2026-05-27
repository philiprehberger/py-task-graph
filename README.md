# philiprehberger-task-graph

[![Tests](https://github.com/philiprehberger/py-task-graph/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-task-graph/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-task-graph.svg)](https://pypi.org/project/philiprehberger-task-graph/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-task-graph)](https://github.com/philiprehberger/py-task-graph/commits/main)

![philiprehberger-task-graph](https://raw.githubusercontent.com/philiprehberger/py-task-graph/main/package-card.webp)

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

### Pass Dependency Results

Pass each dependency's return value as a keyword argument to the task function (named after the dependency).

```python
graph = TaskGraph()
graph.add_task("source", lambda: 7)
graph.add_task("double", lambda source: source * 2, depends=["source"])

results = graph.run(pass_results=True)
# {"source": 7, "double": 14}
```

### Execution Hooks

Register callbacks to observe task execution — useful for logging, metrics, or tracing without modifying the task functions.

```python
graph = TaskGraph()

@graph.on_before_run
def log_start(name: str) -> None:
    print(f"starting {name}")

@graph.on_after_run
def log_done(name: str, result: object, duration: float) -> None:
    print(f"{name} done in {duration:.3f}s -> {result!r}")

@graph.on_error
def log_failure(name: str, exc: BaseException) -> None:
    print(f"{name} failed: {exc!r}")
```

The error hook fires only after all retries have been exhausted; the original exception still propagates after every hook has run.

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
| `graph.run(pass_results=False)` | Execute tasks in topological order; optionally pass dep results as kwargs |
| `graph.run_parallel(max_workers=None, pass_results=False)` | Execute with thread parallelism |
| `graph.dry_run()` | Return execution order without running |
| `graph.on_before_run(hook)` | Register `(name) -> None` callback fired before each task |
| `graph.on_after_run(hook)` | Register `(name, result, duration) -> None` callback fired after each successful task |
| `graph.on_error(hook)` | Register `(name, exc) -> None` callback fired after retries are exhausted |
| `CycleError` | Raised when a dependency cycle is detected |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-task-graph)

🐛 [Report issues](https://github.com/philiprehberger/py-task-graph/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-task-graph/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
