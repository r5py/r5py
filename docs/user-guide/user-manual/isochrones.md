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

Isochrones are lines of equal travel time. They are the boundaries of a
geographic area reachable from a point of origin within a specified amount of
time. Isochrones can be used to answer questions of a spatial accessibility
footprint. They are visually intuitive, can reveal barriers and bottlenecks and
the seemingly teleportative powers of fast public transport. Isochrones are
often used to plan service areas, carry out equity analysis, or select sites for
services.

To compute isochrones in *r5py*, you need a
{class}`TransportNetwork<r5py.TransportNetwork>` and a point of origin. For this
example, we use [the main railway station in
Helsinki](https://en.wikipedia.org/wiki/Helsinki_Central_Station).


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

We then instantiate an {class}`r5py.Isochrones()` object, to which we pass the
transport network, the origin point, a departure
{class}`datetime<datetime.datetime>` and the {class}`transport
modes<r5py.TransportMode>` which will be used for routing. Note that when
multiple origin points or multiple transport modes are specified, the respective
fastest will be recorded in the outputs.

```{code-cell}
import datetime

isochrones = r5py.Isochrones(
    transport_network,
    origins=RAILWAY_STATION,
    departure=datetime.datetime(2022, 2, 22, 8, 30),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
    isochrones=[5, 10, 15],
)
```


{class}`Isochrones<r5py.Isochrones>`, just like
{class}`travel time matrices<r5py.TravelTimeMatrix>` and {class}`detailed
itineraries<r5py.DetailedItineraries>`, inherit from {class}`pandas.DataFrame`
and {class}`geopandas.GeoDataFrame`: all methods and attributes of (geo) data
frames work on isochrone data sets.

The output has two columns: a {class}`MultiLineString<shapely.MultiLineString>` geometry
and the travel time to the geometry as {class}`datetime.Timedelta`:

```{code-cell}
isochrones
```


```{code-cell}
:tags: [remove-input, remove-output]

# hidden from readthedocs,
# converts the travel time column to string, as folium
# has troubles with complex data types

isochrones["travel_time"] = isochrones["travel_time"].apply(str)
```

```{code-cell}
isochrones.explore(column="travel_time", cmap="YlOrRd")
```
