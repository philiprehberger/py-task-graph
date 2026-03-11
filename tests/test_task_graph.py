import pytest
from philiprehberger_task_graph import TaskGraph, CycleError


def test_simple_execution():
    graph = TaskGraph()
    order = []

    @graph.task()
    def a():
        order.append("a")

    @graph.task()
    def b():
        order.append("b")

    graph.run()
    assert set(order) == {"a", "b"}


def test_dependency_order():
    graph = TaskGraph()
    order = []

    @graph.task()
    def fetch():
        order.append("fetch")

    @graph.task(depends_on=["fetch"])
    def process():
        order.append("process")

    @graph.task(depends_on=["process"])
    def save():
        order.append("save")

    graph.run()
    assert order == ["fetch", "process", "save"]


def test_add_task_programmatic():
    graph = TaskGraph()
    results = []
    graph.add_task("a", lambda: results.append("a"))
    graph.add_task("b", lambda: results.append("b"), depends_on=["a"])
    graph.run()
    assert results == ["a", "b"]


def test_cycle_detection():
    graph = TaskGraph()
    graph.add_task("a", lambda: None, depends_on=["b"])
    graph.add_task("b", lambda: None, depends_on=["a"])
    with pytest.raises(CycleError):
        graph.run()


def test_dry_run():
    graph = TaskGraph()
    graph.add_task("a", lambda: None)
    graph.add_task("b", lambda: None, depends_on=["a"])
    graph.add_task("c", lambda: None, depends_on=["b"])
    order = graph.dry_run()
    assert order == ["a", "b", "c"]


def test_parallel_execution():
    graph = TaskGraph()
    results = []
    graph.add_task("a", lambda: results.append("a"))
    graph.add_task("b", lambda: results.append("b"), depends_on=["a"])
    graph.run_parallel(max_workers=2)
    assert results == ["a", "b"]


def test_empty_graph():
    graph = TaskGraph()
    results = graph.run()
    assert results == {}


def test_return_values():
    graph = TaskGraph()
    graph.add_task("a", lambda: 42)
    graph.add_task("b", lambda: "hello")
    results = graph.run()
    assert results["a"] == 42
    assert results["b"] == "hello"
