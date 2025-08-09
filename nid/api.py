from __future__ import annotations

import httpx
from ratelimit import sleep_and_retry, limits

from nid.logger import logger

from diskcache import Cache

cache = Cache("./cache/")


@cache.memoize(expire=60)
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
