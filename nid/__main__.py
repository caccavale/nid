from __future__ import annotations

import json
import pathlib

import click

import logging

from nid.domain import TARGETS, build
from nid.logger import logger

log_levels = [
    level
    for level in logging.getLevelNamesMapping().keys()
    if level.lower() not in ("critical", "warn")
]


@click.command()
@click.argument(
    "targets",
    nargs=-1,
    type=click.Choice(["all", *TARGETS.keys()], case_sensitive=False),
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=pathlib.Path),
    default="./graph.json",
    show_default=True,
)
@click.option("-s", "--sample", type=int, default=-1, show_default=True)
@click.option(
    "-v",
    "--verbose",
    type=click.Choice(log_levels, case_sensitive=False),
    default="warning",
    is_flag=False,
    flag_value="debug",
)
@click.option("-vv", is_flag=True, hidden=True)
def cli(
    targets: tuple[str, ...], sample: int, output: pathlib.Path, verbose: str, vv: bool
):
    """Generate graph.json from TARGETS, defaults to all."""

    configure_logging(verbose, vv)

    graph = build(targets)
    if sample > 0:
        graph = graph.sample(sample)

    if output.exists() and output.is_dir():
        output /= "graph.json"

    output.parent.mkdir(exist_ok=True)
    with open(output, "w") as f:
        json.dump(graph.to_d3(), f)


def configure_logging(verbose: str, vv: bool) -> None:
    if vv:
        verbose = "NOTSET"
        logging.basicConfig(level=logging.NOTSET)

    verbose = verbose.upper()

    logger.setLevel(logging.getLevelNamesMapping()[verbose])
    logger.info(f"Set log level: {verbose}")


if __name__ == "__main__":
    cli()
