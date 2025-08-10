from __future__ import annotations

from collections import defaultdict
from functools import wraps
from typing import Callable, Concatenate, Any

from nid.logger import logger


graph_method = Callable[Concatenate["Graph", ...], Any]


def require_clean(method: graph_method) -> graph_method:
    @wraps(method)
    def wrapper(self: Graph, *args: Any, **kwargs: Any) -> Any:
        if self._dirty:
            logger.info(f"Cleaning graph before {method.__name__}")
            self = self.clean()

        return method(self, *args, **kwargs)

    return wrapper


def mark_dirty(method: graph_method) -> graph_method:
    @wraps(method)
    def wrapper(self: Graph, *args: Any, **kwargs: Any) -> Any:
        self._dirty = True
        return method(self, *args, **kwargs)

    return wrapper


class Graph:
    _nodes: set[str]
    _edges: set[tuple[str, str]]

    _forward: dict[str, set[str]]
    _reverse: dict[str, set[str]]

    _tags: dict[str | tuple[str, str], dict[str, str]]

    # _cardinality: dict[str, int] = field(default_factory=dict)

    _dirty: bool

    def __init__(
        self,
        nodes: set[str] | None = None,
        edges: set[tuple[str, str]] | None = None,
        tags: dict[str | tuple[str, str], dict[str, str]] | None = None,
    ):
        self._nodes = set()
        self._edges = set()

        self._forward = defaultdict(set)
        self._reverse = defaultdict(set)

        self._tags = defaultdict(dict)

        tags = tags or {}

        for node in nodes or []:
            self.add_node(node, tags.get(node))

        for left, right in edges or []:
            self.add_edge(left, right, tags.get((left, right)))

        self._dirty = False

    @mark_dirty
    def add_node(self, node: str, tags: dict[str, str] | None = None):
        self._nodes.add(node)

        if tags:
            self._tags[node].update(tags)

    @mark_dirty
    def add_edge(self, source: str, target: str, tags: dict[str, str] | None = None):
        self._edges.add((source, target))
        self._forward[source].add(target)
        self._reverse[target].add(source)

        if tags:
            self._tags[(source, target)].update(tags)

    def clean(self, exclude_islands=True) -> Graph:
        if exclude_islands:
            nodes = set()

            for node in self._nodes:
                partners = self._forward.get(node, set()) | self._reverse.get(
                    node, set()
                )
                if partners & self._nodes:
                    nodes.add(node)
                else:
                    logger.debug(f"Excluding island: {node}")
        else:
            nodes = self._nodes.copy()

        edges = set()
        for source, target in self._edges:
            if source not in nodes or target not in nodes:
                logger.debug(f"Invalid edge: {source} -> {target}")
                continue

            edges.add((source, target))

        return Graph(nodes, edges, self._tags)

    @require_clean
    def sample(self, sample_size: int) -> Graph:
        nodes: set[str] = set()
        edges: set[tuple[str, str]] = set()

        node_iter = iter(self._nodes)
        target_to_nodes_in_graph: dict[str, set[str]] = defaultdict(set)

        while len(nodes) < min(sample_size, len(self._nodes)):
            if target_to_nodes_in_graph:
                node = next(
                    iter(target_to_nodes_in_graph.keys())
                )  # Get first, does not mutate
            else:
                node = next(node_iter)

            nodes.add(node)

            for target in self._forward.get(node, []):
                if target in nodes:
                    edges.add((node, target))
                else:
                    target_to_nodes_in_graph[target].add(node)

            # Only add node relationships in one direction
            if node in target_to_nodes_in_graph:
                for source in target_to_nodes_in_graph[node]:
                    edges.add((source, node))

                target_to_nodes_in_graph.pop(node)

        return Graph(nodes, edges, self._tags)

    @require_clean
    def to_d3(self) -> dict[str, list[dict[str, str]] | dict[str, list[str]]]:
        nodes = [self._tags.get(node, {}) | {"id": node} for node in self._nodes]
        edges = [
            self._tags.get((source, target), {}) | {"source": source, "target": target}
            for source, target in self._edges
        ]
        outbound = {k: list(v) for k, v in self._forward.items() if v}
        inbound = {k: list(v) for k, v in self._reverse.items() if v}

        return {
            "nodes": nodes,
            "links": edges,
            "outbound": outbound,
            "inbound": inbound,
        }
