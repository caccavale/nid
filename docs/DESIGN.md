
# Goal

put OSRS into a graph.  do not think about usability

ex:
- Monsters <- drop -> items <- craft -> items <- are sold by -> vendors 
- Items <- required for -> quests 
- Skills <- required for -> quests 
- Quests <- required for -> quests
- there are a lot of relationships to add over time we will add node/edge filters we are engineers not designers

# Architecture

## v0

local run fetches a limited graph solely through SMW api calls to categories and properties, e.g. monsters <-drop-> items

## ideal

github runner on chron: compare date to last run (idk write a file), use wiki API for page changes in that time, re-fetch data for those pages to disk cache, mangle into graph, publish to gh pages

# Tech Stack

- github
- python
- FILES (io bound lets cache everything to disk)
- D3 for vis

if ur thinking about introducing more complexity or technology think again

# Constraints
this is not allowed to cost anything

- free tier of gh actions (limited runner time and frequency)
- static ghpages site 
- 1 rps to OSRS wiki api
- 1 rps scraping OSRS wiki

# Resources

- [SimpleMediaWiki](https://runescape.wiki/w/User:Gaz_Lloyd/smw_api#OSRSW)
- [D3 force-directed graph](https://observablehq.com/@d3/force-directed-graph/2), [with filtering](https://gist.github.com/colbenkharrl/dcb5590173931bb594e195020aaa959d)
- <a>https://github.com/Hannah-GBS/runelite-wiki-scraper</a>
- [runelite item icon cache](https://github.com/runelite/static.runelite.net/tree/gh-pages/cache/item/icon)

