# philiprehberger-task-graph

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

@graph.task(depends_on=["fetch_data"])
def process_data():
    return transform()

@graph.task(depends_on=["process_data"])
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
graph.add_task("process", process_fn, depends_on=["fetch"])
graph.add_task("save", save_fn, depends_on=["process"])

# Preview execution order
order = graph.dry_run()
# ["fetch", "process", "save"]
```

### Cycle Detection

```python
from philiprehberger_task_graph import CycleError

# Raises CycleError if dependencies form a cycle
graph.run()
```

## API

- `TaskGraph()` — Create a new task graph
- `@graph.task(depends_on=None)` — Decorator to register a task
- `graph.add_task(name, fn, depends_on=None)` — Add a task programmatically
- `graph.run()` — Execute tasks in topological order
- `graph.run_parallel(max_workers=4)` — Execute with thread parallelism
- `graph.dry_run()` — Return execution order without running

## License

MIT
