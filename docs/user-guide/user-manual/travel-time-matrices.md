---
kernelspec:
  name: python3
  display_name: python3
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: '0.13'
    jupytext_version: 1.14.1
---


# Travel-time matrices

```{code-cell}
:tags: ["remove-input", "remove-output"]

# this cell is hidden from output
# it’s used to set sys.path to point to the local repo,
# and to define a `DATA_DIRECTORY` pathlib.Path
import pathlib
import sys 

NOTEBOOK_DIRECTORY = pathlib.Path().resolve()
DOCS_DIRECTORY = NOTEBOOK_DIRECTORY.parent.parent
DATA_DIRECTORY = DOCS_DIRECTORY / "_static" / "data"
R5PY_DIRECTORY = DOCS_DIRECTORY.parent / "src"
sys.path.insert(0, str(R5PY_DIRECTORY))
```


:::{dropdown} What is a travel time matrix?

A travel time matrix is a tool and data set that allows researchers to study how
easily people can reach different destination within and beyond cities, and how
accessibility is influenced by factors such as the quality of public transport
systems, street networks, and land use patterns. 

Typically, a travel time matrix is a table that shows the travel time (or other
travel costs) between all pairs of a set of locations in an urban area. The
locations represent typical origins and destinations, such as everyday services
and residential homes, or are a complete set of locations covering the entire
area wall-to-wall, such as census polygons or a regular grid.

Travel time matrices can then be used to analyse accessibility patterns,
evaluate the impacts of transport planning and land use policies, and to
identify in which areas and for which groups of people a city works best and
worst. This information can then help cities to become more equitable and more
sustainable, and foster a good quality of life for their residents.

Successful recent research that either used or produced travel time matrices
include the work of the Digital Geography Lab at the University of Helsinki
(e.g., {cite:t}`tenkanen_longitudinal_2020}`, {cite:t}`salonen_modelling_2013`,
or {cite:t}`jarv_dynamic_2018`), the TODO: ADD SOME MORE GROUPS AND RESEARCH
HERE!
:::



:::{bibliography}
:filter: docname in docnames
:::
