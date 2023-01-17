---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.1
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
configuration
advanced-usage
:::

```{code-cell} ipython3
:tags: [remove-input, remove-output]

# this cell is hidden from READTHEDOCS output
# it’s used to set sys.path to point to the local r5py source code,
# and to define a `DATA_DIRECTORY` pathlib.Path
import pathlib
import sys

NOTEBOOK_DIRECTORY = pathlib.Path().resolve()
DOCS_DIRECTORY = NOTEBOOK_DIRECTORY.parent.parent
DATA_DIRECTORY = DOCS_DIRECTORY / "_static" / "data"
R5PY_DIRECTORY = DOCS_DIRECTORY.parent / "src"

sys.path.insert(0, str(R5PY_DIRECTORY))
```

```{code-cell} ipython3
:tags: [remove-input, remove-output]

# also this cell is hidden in READTHEDOCS
# it loads the input geodata for the quickstart example

# (it is hidden, so it does not clutter the message, 
# more detailed information can be found, e.g., in ‘Data requirements’ or
# in the more advanced tutorials)

# if you opened this notebook elsewhere, be sure to run
# this cell, so data is, indeed, read from disk

import geopandas
population_grid = geopandas.read_file(DATA_DIRECTORY / "Helsinki" / "population_grid_2020.gpkg")

import shapely.geometry
RAILWAY_STATION = shapely.geometry.Point(24.941521, 60.170666)
```

The core functionality of *r5py* is to compute travel time matrices for large extents, such as entire cities or countries. This page walks you through the - pleasantly few - steps to do so. In our example below, we work with data from Helsinki, the capital of Finland. We calculate the travel times on public transport or on foot from the centre points of a population grid data set to the city’s main railway stations. 

## Origins and destination

We intend to compute the travel times from the centre points of population grid
cells to the railway station, so we first need to obtain the locations of these
places. 

For this example, we prepared them ahead of time: `population_grid` is a
[`geopandas.GeoDataFrame`](https://geopandas.org/en/stable/docs/user_guide/data_structures.html)
containing a 250 ⨉ 250 m grid covering parts of downtown Helsinki, and obtained
from the [Helsinki Region Environmental Services
(HSY)](https://hri.fi/data/en_GB/dataset/vaestotietoruudukko). The
[constant](https://stackoverflow.com/q/44636868) `RAILWAY_STATION` is a
[`shapely.Point`](https://shapely.readthedocs.io/en/stable/reference/shapely.Point.html),
its coordinates refer to Helsinki’s main railway station in the
[`EPSG:4326`](https://spatialreference.org/ref/epsg/4326/) reference system.

```{code-cell} ipython3
import folium

map = population_grid.explore("population", cmap="Reds")
folium.Marker((RAILWAY_STATION.y, RAILWAY_STATION.x)).add_to(map)
map
```

## Transport network

Virtually all operations of *r5py* require a transport network. The street
network, including infrastructure for cycling and walking, is loaded from an
[OpenStreetMap extract](https://wiki.openstreetmap.org/wiki/Extracts) in
*Protocol Buffer* (`.pbf`) format. The public transport schedule can be read
from a [GTFS](https://en.wikipedia.org/wiki/GTFS) file.

For the quickstart example, you find sample data sets in `DATA_DIRECTORY`
(`/docs/_static/data` in the source repository).

To import the street and public transport networks, instantiate an
`r5py.TransportNetwork` with the file paths to the OSM extract and the GTFS
files:

```{code-cell} ipython3
from r5py import TransportNetwork

transport_network = TransportNetwork(
    DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf",
    [
        DATA_DIRECTORY / "Helsinki" / "GTFS.zip"
    ]
)
```

At this stage, *r5py* has created a routable transport network, that is refered
to by the `transport_network` variable. We can now start using this network for
travel time calculations.

+++

## Compute a travel time matrix

A travel time matrix is a dataset detailing the travel costs (e.g., time)
between given locations (origins and destinations) in a study area.  In *r5py*,
`r5py.TravelTimeMatrixComputer`s calculate these matrices. A
`TravelTimeMatrixComputer`, once initialised, can be used multiple times with
adjusted parameters, such as a different departure time.

To initialise a `TravelTimeMatrixComputer`, the following input arguments are
needed:
- a `transport_network`, such as the one we just created,
- `origins`, a `geopandas.GeoDataFrame` with one or more points representing the
  departure points of routes, 
- `destinations`, a `geopandas.GeoDataFrame` with one or more points
  representing the destinations of routes, 
- `departure`, a [`datetime.datetime`](docs.python.org/3/library/datetime.html)
  refering to the departure date and time for routing, and
- `transport_modes`, a list of `r5py.TransitMode`s and `r5py.LegMode`s which
  determines the travel modes that will be used in the calculations. 



These can
be passed using the options from the `TransitMode` and `LegMode` classes.


  - *Hint*: To see all available options, run `help(TransitMode)` or
    `help(LegMode)`.


   - *Note*: By default, `r5py` summarizes and calculates a median travel time from all possible connections within one hour from given depature time (with 1 minute frequency). It is possible to adjust this time window using `departure_time_window` parameter ([see details here](r5py.RegionalTask)).

:::{note} In addition to these ones, the constructor also accepts many other parameters [listed here](https://r5py.readthedocs.io/en/stable/reference.html#r5py.RegionalTask), such as walking and cycling speed, maximum trip duration, maximum number of transit connections used during the trip, etc.
:::

Now, we will first create a `travel_time_matrix_computer` instance as described above:

```{code-cell} ipython3
import datetime
import r5py

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
        r5py.TransitMode.TRANSIT,
        r5py.LegMode.WALK,
    ],
)
```

Running this initializes the `TravelTimeMatrixComputer`, but any calculations were not done yet.
To actually run the computations, we need to call `.compute_travel_times()` on the instance, which will calculate the travel times between all points:

```{code-cell} ipython3
travel_times = travel_time_matrix_computer.compute_travel_times()
travel_times.head()
```

As a result, this returns a `pandas.DataFrame` which we stored in the `travel_time_matrix` variable. The values in the `travel_time` column are travel times in minutes between the points identified by `from_id` and `to_id`. As you can see, the `id` value in the `from_id` column is the same for all rows because we only used one origin location as input.

To get a better sense of the results, let's create a travel time map based on our results. We can do this easily by making a table join between the `points` GeoDataFrame and the `travel_time_matrix`. The key in the `travel_time_matrix` table is the column `to_id` and the corresponding key in `points` GeoDataFrame is the column `id`:

```{code-cell} ipython3
travel_times = population_grid.merge(travel_times, left_on="id", right_on="from_id")
travel_times.head()
```

Now we have the travel times attached to each point, and we can easily visualize them on a map:

```{code-cell} ipython3
travel_times.explore("travel_time", cmap="Greens")
```
