"""Lightweight task dependency engine with topological execution."""

from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from typing import Any, Callable


__all__ = [
    "TaskGraph",
    "CycleError",
]


class CycleError(Exception):
    """Raised when a dependency cycle is detected in the task graph."""


@dataclass
class _Task:
    name: str
    fn: Callable[..., Any]
    depends: list[str] = field(default_factory=list)
    timeout: float | None = None
    retries: int = 0


class TaskGraph:
    """A directed acyclic graph of tasks with dependency-aware execution.

    Tasks are registered via the :meth:`task` decorator or :meth:`add_task`,
    then executed in topological order with :meth:`run`.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, _Task] = {}

    def task(
        self,
        name: str | None = None,
        depends: list[str] | None = None,
        timeout: float | None = None,
        retries: int = 0,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a task.

        Args:
            name: Task name. Defaults to the function name.
            depends: List of task names this task depends on.
            timeout: Maximum execution time in seconds. Raises ``TimeoutError`` if exceeded.
            retries: Number of times to retry on failure before propagating the exception.
        """
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            task_name = name or fn.__name__
            self.add_task(task_name, fn, depends, timeout=timeout, retries=retries)
            return fn
        return decorator

    def add_task(
        self,
        name: str,
        fn: Callable[..., Any],
        depends: list[str] | None = None,
        timeout: float | None = None,
        retries: int = 0,
    ) -> None:
        """Register a task imperatively.

        Args:
            name: Unique task name.
            fn: Callable to execute.
            depends: List of task names this task depends on.
            timeout: Maximum execution time in seconds. Raises ``TimeoutError`` if exceeded.
            retries: Number of times to retry on failure before propagating the exception.
        """
        self._tasks[name] = _Task(
            name=name, fn=fn, depends=depends or [],
            timeout=timeout, retries=retries,
        )

    def _execute_task(self, task: _Task) -> Any:
        """Execute a single task with timeout and retry support."""
        last_exc: BaseException | None = None
        attempts = 1 + task.retries

        for _ in range(attempts):
            try:
                if task.timeout is not None:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future: Future[Any] = executor.submit(task.fn)
                        try:
                            return future.result(timeout=task.timeout)
                        except TimeoutError:
                            raise
                else:
                    return task.fn()
            except Exception as exc:
                last_exc = exc

        raise last_exc  # type: ignore[misc]

    def get_order(self) -> list[str]:
        """Return task names in topological execution order.

        Raises:
            CycleError: If a dependency cycle is detected.
            ValueError: If a dependency references an unknown task.
        """
        in_degree: dict[str, int] = {name: 0 for name in self._tasks}
        adjacency: dict[str, list[str]] = {name: [] for name in self._tasks}

        for name, task in self._tasks.items():
            for dep in task.depends:
                if dep not in self._tasks:
                    msg = f"Task '{name}' depends on unknown task '{dep}'"
                    raise ValueError(msg)
                adjacency[dep].append(name)
                in_degree[name] += 1

        queue: deque[str] = deque()
        for name, degree in in_degree.items():
            if degree == 0:
                queue.append(name)

        order: list[str] = []
        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self._tasks):
            remaining = set(self._tasks) - set(order)
            msg = f"Dependency cycle detected involving: {', '.join(sorted(remaining))}"
            raise CycleError(msg)

        return order

    def dry_run(self) -> list[str]:
        """Return the execution order without running any tasks.

        Returns:
            List of task names in execution order.
        """
        return self.get_order()

    def run(self) -> dict[str, Any]:
        """Execute all tasks in topological order.

        Returns:
            Dict mapping task names to their return values.
        """
        order = self.get_order()
        results: dict[str, Any] = {}

        for name in order:
            task = self._tasks[name]
            results[name] = self._execute_task(task)

        return results

    def run_parallel(self, max_workers: int | None = None) -> dict[str, Any]:
        """Execute tasks concurrently, respecting dependency order.

        Tasks without dependencies run in parallel. A task only starts
        after all its dependencies have completed.

        Args:
            max_workers: Maximum number of threads. Defaults to ThreadPoolExecutor default.

        Returns:
            Dict mapping task names to their return values.
        """
        order = self.get_order()
        results: dict[str, Any] = {}
        futures: dict[str, Future[Any]] = {}

        in_degree: dict[str, int] = {name: 0 for name in self._tasks}
        dependents: dict[str, list[str]] = {name: [] for name in self._tasks}

        for name, task in self._tasks.items():
            for dep in task.depends:
                dependents[dep].append(name)
                in_degree[name] += 1

        ready: deque[str] = deque()
        for name in order:
            if in_degree[name] == 0:
                ready.append(name)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            pending: set[str] = set()

            while ready or pending:
                while ready:
                    name = ready.popleft()
                    task = self._tasks[name]
                    futures[name] = executor.submit(self._execute_task, task)
                    pending.add(name)

                done = {n for n in pending if futures[n].done()}
                if not done and pending:
                    next_done = next(iter(pending))
                    futures[next_done].result()
                    done = {n for n in pending if futures[n].done()}

                for name in done:
                    pending.discard(name)
                    results[name] = futures[name].result()
                    for dep_name in dependents[name]:
                        in_degree[dep_name] -= 1
                        if in_degree[dep_name] == 0:
                            ready.append(dep_name)

        return results
