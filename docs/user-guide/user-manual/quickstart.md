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

The core functionality of *r5py* is to compute travel time matrices for large extents, such as entire cities or countries. This page walks you through the - pleasantly few - steps to do so.

## Load the origin and destination data

Let's start by downloading a sample point dataset into a geopandas `GeoDataFrame` that we can use as our origin and destination locations. For the sake of this exercise, we have prepared a grid of points covering parts of Helsinki. The point data also contains the number of residents of each 250 meter cell:

```{code-cell} ipython3
import geopandas

population_grid = geopandas.read_file(DATA_DIRECTORY / "Helsinki" / "population_grid_2020.gpkg")
population_grid.head()
```

The `points` GeoDataFrame contains a few columns, namely `id`, `population` and `geometry`. The `id` column with unique values and `geometry` columns are required for `r5py` to work. If your input point dataset does not have an `id` column with unique values, `r5py` will throw an error.

To get a better sense of the data, let's create a map that shows the locations of the points and visualise the number of people living in each cell (the cells are represented by their centre point):

```{code-cell} ipython3
map = population_grid.explore("population", cmap="Reds")
map
```

Let's pick one of these points to represent our **origin** and store it in a separate GeoDataFrame:

```{code-cell} ipython3
import shapely.geometry
RAILWAY_STATION = shapely.geometry.Point(24.941521, 60.170666)
```

```{code-cell} ipython3
import folium

folium.Marker((RAILWAY_STATION.y, RAILWAY_STATION.x)).add_to(map)
map
```

## Load transport network

Virtually all operations of `r5py` require a transport network. In this example, we use data from Helsinki metropolitan area, which you can find in the source code repository of r5py in `docs/data/` [(see here)](https://github.com/r5py/r5py/tree/main/docs/data). To import the street and public transport networks, instantiate an `r5py.TransportNetwork` with the file paths to the OSM extract and the GTFS files:

```{code-cell} ipython3
from r5py import TransportNetwork

transport_network = TransportNetwork(
    DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf",
    [
        DATA_DIRECTORY / "Helsinki" / "GTFS.zip"
    ]
)
```

At this stage, `r5py` has created the routable transport network and it is stored in the `transport_network` variable. We can now start using this network for doing the travel time calculations.


## Compute travel time matrix from one to all locations

A travel time matrix is a dataset detailing the travel costs (e.g., time) between given locations (origins and destinations) in a study area. To compute a travel time matrix with `r5py` based on public transportation, we first need to initialize an `r5py.TravelTimeMatrixComputer` object. As inputs, we pass following arguments for the `TravelTimeMatrixComputer`:
- `transport_network`, which we created in the previous step representing the routable transport network.
- `origins`, which is a GeoDataFrame with one location that we created earlier (however, you can also use multiple locations as origins).
- `destinations`, which is a GeoDataFrame representing the destinations (in our case, the `points` GeoDataFrame).
- `departure`, which should be Python's `datetime` object (in our case standing for "22nd of February 2022 at 08:30") to tell `r5py` that the schedules of this specific time and day should be used for doing the calculations.
   - *Note*: By default, `r5py` summarizes and calculates a median travel time from all possible connections within one hour from given depature time (with 1 minute frequency). It is possible to adjust this time window using `departure_time_window` parameter ([see details here](r5py.RegionalTask)).
- `transport_modes`, which determines the travel modes that will be used in the calculations. These can be passed using the options from the `TransitMode` and `LegMode` classes.
  - *Hint*: To see all available options, run `help(TransitMode)` or `help(LegMode)`.

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
