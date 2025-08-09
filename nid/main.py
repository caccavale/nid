from __future__ import annotations

import json
import os

import click
import httpx

import logging

from ratelimit import sleep_and_retry, limits

logging.basicConfig(level=logging.NOTSET)

logger = logging.getLogger()


@sleep_and_retry
@limits(calls=1, period=1)
def perform_query(params) -> dict:
    response = httpx.get(
        "https://oldschool.runescape.wiki/api.php",
        headers={"user-agent": "nid (@bouk on discord)"},
        params=params,
        timeout=10,
    )

    if not response.status_code == 200:
        raise Exception(response.status_code, response.text)

    if "error" in (body := response.json()):
        raise Exception(200, body)

    return body.get("query", {}).get("results")


def perform_pagename_paginated_smw_query(
    selections, printouts=None, page_size=10000, max_pages=0, delay=1.0
) -> dict:
    printouts = f"|{printouts}" if printouts else ""

    def build_query(last_page=None):
        last_page = f"|[[>>{last_page}]]" if last_page else ""
        return f"{selections}{last_page}{printouts}|limit={page_size}"

    def build_params(query):
        return {
            "format": "json",
            "action": "ask",
            "query": query,
        }

    def query_with_debug(last_page=None) -> tuple[dict, str]:
        query = build_query(last_page)
        params = build_params(query)
        logger.debug(f"Querying {query}...")
        _results = perform_query(params)
        new_last = list(_results.keys())[-1]
        logger.debug(
            f"...complete, fetched {len(_results)} results ({last_page or ' '}, {new_last}]"
        )
        return _results, new_last

    results, cursor = query_with_debug()

    page = 1
    while max_pages == 0 or page < max_pages:
        more, cursor = query_with_debug(cursor)
        results.update(more)
        logger.debug(f"\t...up to {len(results)} results.")
        page += 1

        if len(more) < page_size:
            break

    return results


class Graph:
    _nodes: set[str]
    _edges: set[tuple[str, str]]
    _dirty: bool = False

    def __init__(
        self, nodes: set[str] | None = None, edges: set[tuple[str, str]] | None = None
    ):
        self._nodes = nodes if nodes else set()
        self._edges = edges if edges else set()

    def add_node(self, node: str):
        self._nodes.add(node)
        self._dirty = True

    def add_edge(self, source: str, target: str):
        self._edges.add((source, target))
        self._dirty = True

    def clean(self, exclude_islands=True) -> Graph:
        sources, targets = zip(*self._edges)

        nodes = set()
        for node in self._nodes:
            if exclude_islands and not (node in sources or node in targets):
                logger.debug(f"Excluding island: {node}")
                continue

            nodes.add(node)

        edges = set()
        for source, target in self._edges:
            if source not in nodes or target not in nodes:
                logger.debug(f"Invalid edge: {source} -> {target}")
                continue

            edges.add((source, target))

        return Graph(nodes, edges)

    def to_d3(self) -> dict[str, list[dict[str, str]]]:
        if self._dirty:
            logger.warning("Calling export method on unclean graph")
            return self.clean().to_d3()

        nodes = [{"id": node} for node in self._nodes]
        edges = [{"source": source, "target": target} for source, target in self._edges]

        return {"nodes": nodes, "links": edges}


def graph_of_production(graph: Graph | None) -> Graph:
    graph = graph or Graph()

    production_data = perform_pagename_paginated_smw_query(
        "[[Category:Items]]", "?Production JSON|?Uses material"
    )

    for name, value in production_data.items():
        graph.add_node(name)

        for use in value.get("printouts", {}).get("Uses material", []):
            graph.add_edge(use.get("fulltext"), name)

    return graph


def graph_of_drops(graph: Graph | None) -> Graph:
    graph = graph or Graph()

    drop_data = perform_pagename_paginated_smw_query("[[Drop JSON::+]]", "?Drop JSON")

    for value in drop_data.values():
        if drop_json := value.get("printouts", {}).get("Drop JSON", [None])[0]:
            drop = json.loads(drop_json)

            source = drop.get("Dropped from")
            target = drop.get("Dropped item")

            if source and target:
                graph.add_node(source)
                graph.add_node(target)
                graph.add_edge(source, target)

    return graph


relationships = {"drops": graph_of_drops, "production": graph_of_production}


@click.command()
@click.argument("targets", nargs=-1)
def generate_data(targets: tuple[str, ...]):
    """Generate graph.json.

    TARGETS can be any combination of [production, drops, or all], defaults to "all"
    """
    targets = targets or ("all",)
    targets = tuple(target.lower() for target in targets)

    graph = Graph()

    if "all" in targets:
        targets = tuple(relationships.keys())

    for target in targets:
        if target in relationships:
            graph = relationships[target](graph)
        else:
            logger.error(f"No target: {target}")

    os.makedirs("./out", exist_ok=True)
    with open("./out/graph.json", "w") as f:
        json.dump(graph.clean().to_d3(), f)


if __name__ == "__main__":
    generate_data()
