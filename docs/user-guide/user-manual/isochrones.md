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

TODO: Write an introduction to what isochrones are


```{code-cell}
:tags: [remove-output]

import r5py
import r5py.sampledata.helsinki
import shapely

transport_network = r5py.TransportNetwork(
    r5py.sampledata.helsinki.osm_pbf,
    [
        r5py.sampledata.helsinki.gtfs,
    ]
)

RAILWAY_STATION = shapely.Point(24.941521, 60.170666)
```

```{code-cell}
import datetime

isochrones = r5py.Isochrones(
    transport_network,
    origins=RAILWAY_STATION,
    departure=datetime.datetime(2022, 2, 22, 8, 30),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    isochrones=[5, 10, 15],
)

isochrones
```

```{code-cell}
isochrones.explore()
```
