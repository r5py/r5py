---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.2
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

```{code-cell}
:tags: [remove-input, remove-output]

# this cell is hidden from READTHEDOCS output
# it’s used to
#    - force pandas to show all columns of the (very wide)
#      result data set

import pandas
pandas.set_option("display.max_columns", None)
```

```{code-cell}
:tags: [remove-input, remove-output]

# also this cell is hidden from READTHEDOCS output
# it’s used to set a stricter memory limit in binderhub notebooks
# as otherwise, the examples would fail

import os

if "MEM_LIMIT" in os.environ:  # binder/kubernetes!
    max_memory = int(os.environ["MEM_LIMIT"]) / 2
    sys.argv.extend(["--max-memory", f"{max_memory}"])
```

# Compute isochrones

Isochrones are geographical lines that represent points of equal travel time from a specific location. They are used to visualize how far you can travel within a given time frame from a starting point, usually by a specific mode of transport like walking, driving, or public transit.

For example, if you want to see all the areas you can reach within a 10-minute walk from your house, the isochrone would show a boundary that connects all locations you could get to in that time. Isochrones are useful in various fields, including urban planning, transportation, and logistics, as they help understand accessibility, identify service gaps, and optimize routes.

In transportation modeling, isochrones can also help to show how areas are connected by infrastructure, or how long it takes to get from one place to another under different conditions.
TODO
