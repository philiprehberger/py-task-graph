"""Tests for philiprehberger_task_graph."""

from __future__ import annotations

import time

import pytest

from philiprehberger_task_graph import TaskGraph, CycleError


def test_imports() -> None:
    from philiprehberger_task_graph import TaskGraph, CycleError  # noqa: F811

    assert TaskGraph is not None
    assert CycleError is not None


class TestTaskGraph:
    def test_single_task(self) -> None:
        g = TaskGraph()
        g.add_task("a", lambda: 1)
        results = g.run()
        assert results == {"a": 1}

    def test_linear_dependency(self) -> None:
        order: list[str] = []
        g = TaskGraph()
        g.add_task("a", lambda: order.append("a"))
        g.add_task("b", lambda: order.append("b"), depends=["a"])
        g.add_task("c", lambda: order.append("c"), depends=["b"])
        g.run()
        assert order == ["a", "b", "c"]

    def test_diamond_dependency(self) -> None:
        order: list[str] = []
        g = TaskGraph()
        g.add_task("a", lambda: order.append("a"))
        g.add_task("b", lambda: order.append("b"), depends=["a"])
        g.add_task("c", lambda: order.append("c"), depends=["a"])
        g.add_task("d", lambda: order.append("d"), depends=["b", "c"])
        g.run()
        assert order[0] == "a"
        assert order[-1] == "d"
        assert set(order[1:3]) == {"b", "c"}

    def test_cycle_detection(self) -> None:
        g = TaskGraph()
        g.add_task("a", lambda: None, depends=["b"])
        g.add_task("b", lambda: None, depends=["a"])
        with pytest.raises(CycleError):
            g.run()

    def test_unknown_dependency(self) -> None:
        g = TaskGraph()
        g.add_task("a", lambda: None, depends=["missing"])
        with pytest.raises(ValueError, match="unknown task"):
            g.run()

    def test_get_order(self) -> None:
        g = TaskGraph()
        g.add_task("b", lambda: None, depends=["a"])
        g.add_task("a", lambda: None)
        order = g.get_order()
        assert order.index("a") < order.index("b")

    def test_dry_run(self) -> None:
        g = TaskGraph()
        g.add_task("a", lambda: None)
        g.add_task("b", lambda: None, depends=["a"])
        order = g.dry_run()
        assert order == ["a", "b"]

    def test_decorator(self) -> None:
        g = TaskGraph()

        @g.task()
        def my_task() -> int:
            return 42

        results = g.run()
        assert results["my_task"] == 42

    def test_decorator_with_name(self) -> None:
        g = TaskGraph()

        @g.task(name="custom")
        def my_task() -> int:
            return 99

        results = g.run()
        assert results["custom"] == 99

    def test_run_parallel(self) -> None:
        g = TaskGraph()
        g.add_task("a", lambda: 1)
        g.add_task("b", lambda: 2, depends=["a"])
        results = g.run_parallel(max_workers=2)
        assert results == {"a": 1, "b": 2}


class TestTimeout:
    def test_task_completes_within_timeout(self) -> None:
        g = TaskGraph()
        g.add_task("fast", lambda: 42, timeout=5.0)
        results = g.run()
        assert results == {"fast": 42}

    def test_task_exceeds_timeout(self) -> None:
        g = TaskGraph()
        g.add_task("slow", lambda: time.sleep(10), timeout=0.1)
        with pytest.raises(TimeoutError):
            g.run()

    def test_decorator_with_timeout(self) -> None:
        g = TaskGraph()

        @g.task(timeout=5.0)
        def quick() -> str:
            return "done"

        results = g.run()
        assert results["quick"] == "done"

    def test_timeout_metadata_stored(self) -> None:
        g = TaskGraph()
        g.add_task("t", lambda: None, timeout=3.5)
        assert g._tasks["t"].timeout == 3.5


class TestRetries:
    def test_succeeds_without_retry(self) -> None:
        g = TaskGraph()
        g.add_task("ok", lambda: 1, retries=2)
        results = g.run()
        assert results == {"ok": 1}

    def test_retries_on_failure_then_succeeds(self) -> None:
        attempts = {"count": 0}

        def flaky() -> str:
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("not yet")
            return "success"

        g = TaskGraph()
        g.add_task("flaky", flaky, retries=2)
        results = g.run()
        assert results == {"flaky": "success"}
        assert attempts["count"] == 3

    def test_retries_exhausted_raises(self) -> None:
        def always_fail() -> None:
            raise RuntimeError("fail")

        g = TaskGraph()
        g.add_task("bad", always_fail, retries=2)
        with pytest.raises(RuntimeError, match="fail"):
            g.run()

    def test_decorator_with_retries(self) -> None:
        attempts = {"count": 0}
        g = TaskGraph()

        @g.task(retries=1)
        def flaky() -> str:
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise ValueError("retry me")
            return "ok"

        results = g.run()
        assert results["flaky"] == "ok"

    def test_retries_metadata_stored(self) -> None:
        g = TaskGraph()
        g.add_task("t", lambda: None, retries=5)
        assert g._tasks["t"].retries == 5


class TestPassResults:
    def test_single_dependency_passes_result(self) -> None:
        g = TaskGraph()
        g.add_task("source", lambda: 7)
        g.add_task("double", lambda source: source * 2, depends=["source"])
        results = g.run(pass_results=True)
        assert results == {"source": 7, "double": 14}

    def test_multiple_dependencies_pass_results(self) -> None:
        g = TaskGraph()
        g.add_task("a", lambda: 3)
        g.add_task("b", lambda: 4)
        g.add_task("sum", lambda a, b: a + b, depends=["a", "b"])
        results = g.run(pass_results=True)
        assert results["sum"] == 7

    def test_pass_results_off_by_default(self) -> None:
        g = TaskGraph()
        g.add_task("a", lambda: 1)
        # Function takes no args; default behavior must not pass kwargs.
        g.add_task("b", lambda: 2, depends=["a"])
        results = g.run()
        assert results == {"a": 1, "b": 2}

    def test_pass_results_in_parallel(self) -> None:
        g = TaskGraph()
        g.add_task("a", lambda: 10)
        g.add_task("b", lambda a: a + 5, depends=["a"])
        results = g.run_parallel(max_workers=2, pass_results=True)
        assert results == {"a": 10, "b": 15}
