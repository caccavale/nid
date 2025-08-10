from __future__ import annotations

import json

from nid.api import perform_pagename_paginated_smw_query
from nid.graph import Graph
from nid.logger import logger


def graph_of_production(graph: Graph | None) -> Graph:
    graph = graph or Graph()

    production_data = perform_pagename_paginated_smw_query(
        "[[Category:Items]]", "?Production JSON|?Uses material"
    )

    for name, value in production_data.items():
        graph.add_node(name, {"type": "item"})

        for use in value.get("printouts", {}).get("Uses material", []):
            graph.add_edge(use.get("fulltext"), name, {"type": "production"})

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
                graph.add_node(source, {"type": "monster"})
                graph.add_node(target, {"type": "item"})
                graph.add_edge(source, target, {"type": "drop"})

    return graph


TARGETS = {"drops": graph_of_drops, "production": graph_of_production}


def build_single(target: str, graph: Graph | None) -> Graph:
    graph = graph or Graph()

    if target in TARGETS:
        return TARGETS[target](graph)

    logger.error(f"No target: {target}")
    return graph


def build(targets: tuple[str, ...]) -> Graph:
    targets = targets or ("all",)
    targets = tuple(target.lower() for target in targets)

    if "all" in targets:
        targets = tuple(TARGETS.keys())

    graph = Graph()
    for target in targets:
        graph = build_single(target, graph)

    return graph
