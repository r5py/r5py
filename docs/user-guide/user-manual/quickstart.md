---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.6
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---


# Quickstart


+++ {"jupyter": {"source_hidden": true}}

:::{toctree}
:maxdepth: 1
:caption: User Manual
:hidden:

self
data-requirements
travel-time-matrices
Detailed itineraries <detailed-itineraries>
advanced-use
configuration
:::


```{code-cell}
:tags: [remove-input, remove-output]

# this cell is hidden from READTHEDOCS output
# it’s used to set sys.path to point to the local *r5py* source code,
# and to define a `DATA_DIRECTORY` pathlib.Path
import pathlib
import sys

NOTEBOOK_DIRECTORY = pathlib.Path().resolve()
DOCS_DIRECTORY = NOTEBOOK_DIRECTORY.parent.parent
DATA_DIRECTORY = DOCS_DIRECTORY / "_static" / "data"
R5PY_DIRECTORY = DOCS_DIRECTORY.parent / "src"

sys.path.insert(0, str(R5PY_DIRECTORY))
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

One of the core functionalities of *r5py* is to compute travel time matrices
efficiently, and for large extents such as entire cities or countries. This
page walks you through the - pleasantly few - steps required to do so.

In our example below, we work with sample data from Helsinki, the capital of
Finland.  We calculate the travel times on public transport or on foot from all
cells in a population grid data set to the city’s main railway station.


## Origins and destination

As we intend to compute the travel times from the centre points of population grid
cells to the railway station, we need to know the locations of these places. 

For this example, we prepared the data ahead of time: `population_grid` is a
[`geopandas.GeoDataFrame`](https://geopandas.org/en/stable/docs/user_guide/data_structures.html)
containing a 250 ⨉ 250 m grid covering parts of downtown Helsinki, and obtained
from the [Helsinki Region Environmental Services
(HSY)](https://hri.fi/data/en_GB/dataset/vaestotietoruudukko). The
[constant](https://stackoverflow.com/q/44636868) `RAILWAY_STATION` is a
[`shapely.Point`](https://shapely.readthedocs.io/en/stable/reference/shapely.Point.html),
its coordinates refer to Helsinki’s main railway station in the
[`EPSG:4326`](https://spatialreference.org/ref/epsg/4326/) reference system.

```{code-cell}
import geopandas
population_grid = geopandas.read_file(DATA_DIRECTORY / "Helsinki" / "population_grid_2020.gpkg")

import shapely
RAILWAY_STATION = shapely.Point(24.941521, 60.170666)
```

```{code-cell}
import folium
import geopandas
import shapely

overview_map = population_grid.explore("population", cmap="Reds")
folium.Marker((RAILWAY_STATION.y, RAILWAY_STATION.x)).add_to(overview_map)
overview_map
```


## Transport network

Virtually all operations of *r5py* require a transport network. *R5py*
understands and reads the following types of transport networks:

- a street network, including infrastructure for cycling and walking, is
  loaded from an [OpenStreetMap
  extract](https://wiki.openstreetmap.org/wiki/Extracts) in *Protocol Buffer*
  (`.pbf`) format (mandatory)
- a public transport schedule from one or more
  [GTFS](https://en.wikipedia.org/wiki/GTFS) files (optional).

For the quickstart example, you find sample data sets in the `DATA_DIRECTORY`
([`docs/_static/data`](https://github.com/r5py/r5py/tree/main/docs/_static/data/)
in the source code repository).

To import the street and public transport networks, instantiate an
{class}`r5py.TransportNetwork` with the file paths to the OSM extract and to
zero or more GTFS files:

```{code-cell}
:tags: ["remove-output"]

import r5py

transport_network = r5py.TransportNetwork(
    DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf",
    [
        DATA_DIRECTORY / "Helsinki" / "GTFS.zip",
    ]
)
```

At this stage, *r5py* has created a routable transport network, that is stored
in the `transport_network` variable. We can now use this network for travel time
calculations. Depending on the extent of the network, this step can take up to
several minutes. However, you can reuse the same `TransportNetwork` instance in
subsequent analyses.


## Compute a travel time matrix

A travel time matrix is a dataset of the travel costs (typically, time) between
given locations (origins and destinations) in a study area.  In *r5py*,
{class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>`s calculate
these matrices. A
{class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>`, once
initialised, can be used multiple times, for instance, with adjusted parameters,
such as a different departure time.

A {class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>` needs (at least)
the following input arguments:
- a `transport_network` ({class}`r5py.TransportNetwork`), such as the one we
  just created,
- `origins`, a {class}`geopandas.GeoDataFrame` with one or more points
  representing the departure points of routes, 
- `destinations`, a {class}`geopandas.GeoDataFrame` with one or more points
  representing the destinations of routes, 
- `departure`, a {class}`datetime.datetime`
  refering to the departure date and time for routing, and
- `transport_modes`, a list of {class}`r5py.TransportMode`s: the travel modes
  that will be used in the calculations

Once instantiated, call
{meth}`TravelTimeMatrixComputer.compute_travel_times()<r5py.TravelTimeMatrixComputer.compute_travel_times()>`
to carry out the actual analysis.

```{code-cell}
:tags: ["remove-output"]

import datetime

origins = population_grid.copy()
origins.geometry = origins.geometry.centroid

destinations = geopandas.GeoDataFrame(
        {
            "id": [1],
            "geometry": [RAILWAY_STATION]
        },
        crs="EPSG:4326",
)

travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
    transport_network,
    origins=origins,
    destinations=destinations,
    departure=datetime.datetime(2022, 2, 22, 8, 30),
    transport_modes=[
        r5py.TransportMode.TRANSIT,
        r5py.TransportMode.WALK,
    ],
)
```

```{code-cell}
travel_times = travel_time_matrix_computer.compute_travel_times()
travel_times.head()
```

The result of
{meth}`compute_travel_times()<r5py.TravelTimeMatrixComputer.compute_travel_times()>`
is a {class}`pandas.DataFrame`. The values in its `travel_time` column are
travel times in minutes between the points identified by `from_id` and `to_id`
(the IDs of the origins and destinations, respectively). As you can see, the
`id` value in the `to_id` column is the same for all rows because our example
used only one destination point (the railway station).


## Save results

If you want to continue analysis later, in a different environment, or simply
retain a clean copy of the results, save the travel time matrix to a CSV file.
Simply use the {meth}`to_csv()<pandas.DataFrame.to_csv()>` method of pandas data
frames:

```{code-cell}
travel_times.to_csv(DATA_DIRECTORY / "travel_times_to_helsinki_railway_station.csv")
```


## Plot a result map

To quickly plot the results in a map, *join* the `travel_times` with the input
data set `population_grid` and
{meth}`explore()<geopandas.GeoDataFrame.explore()>` the joint data frame’s
data.

```{code-cell}
travel_times = population_grid.merge(travel_times, left_on="id", right_on="from_id")
travel_times.head()
```

```{code-cell}
travel_times.explore("travel_time", cmap="Greens")
```
