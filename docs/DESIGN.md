
# Goal

shitpost OSRS into a graph.  

- Monsters <- drop -> items <- craft -> items <- are sold by -> vendors 
- Items <- required for -> quests 
- Skills <- required for -> quests 
- Quests <- required for -> quests


# Architecture

github runner on chron: compare date to last run (idk write a file), check wiki for page changes in that time, re-fetch data for those pages, mangle into graph, publish to gh pages

# Tech Stack

- github
- python
- FILES (io bound lets cache everything to disk)
- D3 for vis

if ur thinking about introducing more complexity or technology think again

# Constraints

free tier of gh actions, static ghpages site (this is not allowed to cost anything)

1 rps to OSRS api, 

# Resources

- [SimpleMediaWiki](https://runescape.wiki/w/User:Gaz_Lloyd/smw_api#OSRSW)
- [D3 force-directed graph](https://observablehq.com/@d3/force-directed-graph/2), [with filtering](https://gist.github.com/colbenkharrl/dcb5590173931bb594e195020aaa959d)
- <a>https://github.com/Hannah-GBS/runelite-wiki-scraper</a>
- [runelite item icon cache](https://github.com/runelite/static.runelite.net/tree/gh-pages/cache/item/icon)

