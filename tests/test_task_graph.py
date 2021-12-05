"""Tests for philiprehberger_task_graph."""

from __future__ import annotations

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
