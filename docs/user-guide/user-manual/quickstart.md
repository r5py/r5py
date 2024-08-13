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
# it’s used to set a stricter memory limit in binderhub notebooks
# as, otherwise, the examples would fail

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

:::{admonition} Sample data set
:class: info

For this example, we prepared the data ahead of time. If you repeat the code
examples independently, [install
`r5py.sampledata.helsinki`](../installation/installation.md#sample-data-sets).

`r5py.sampledata.helsinki.population_grid` is a vector data set in [GeoPackage
(GPKG)](http://www.opengeospatial.org/standards/geopackage) format containing a
250 ⨉ 250 m grid covering parts of downtown Helsinki, and obtained from the
[Helsinki Region Environmental Services
(HSY)](https://hri.fi/data/en_GB/dataset/vaestotietoruudukko).

:::

We open the sample data set file using {meth}`geopandas.GeoDataFrame.read_file()`.

Because, in our example, we only use one destination, the railway station, we
define its location as a {class}`geopandas.GeoDataFrame` containing one
geometry, a {class}`shapely.Point`, the coordinates of which refer to Helsinki’s
main railway station in the
[`EPSG:4326`](https://spatialreference.org/ref/epsg/4326/) reference system.

```{code-cell}
import geopandas
import r5py.sampledata.helsinki
import shapely

population_grid = geopandas.read_file(r5py.sampledata.helsinki.population_grid)

railway_station = geopandas.GeoDataFrame(
    {
        "id": ["railway_station"],
        "geometry": [shapely.Point(24.94152, 60.17066)]
    },
    crs="EPSG:4326",
)
```

```{code-cell}
overview_map = population_grid.explore("population", cmap="Reds")
overview_map = railway_station.explore(m=overview_map, marker_type="marker")
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

For the quickstart example, you find sample data sets in the
`r5py.sampledata.helsinki` package (see [above](#origins-and-destination)).

To import the street and public transport networks, instantiate an
{class}`r5py.TransportNetwork` with the file paths to the OSM extract and to
zero or more GTFS files. With the sample data set, the file paths are in the
`r5py.sampledata.helsinki` namespace:

```{code-cell}
:tags: ["remove-output"]

import r5py
import r5py.sampledata.helsinki

transport_network = r5py.TransportNetwork(
    r5py.sampledata.helsinki.osm_pbf,
    [r5py.sampledata.helsinki.gtfs],
)
```

At this stage, *r5py* has created a routable transport network, that is stored
in the `transport_network` variable. We can now use this network for travel time
calculations. Depending on the extent of the network, this step can take up to
several minutes. Once loaded, you can reuse the same `TransportNetwork` instance
in subsequent analyses.


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

```{code-cell}
:tags: ["remove-output"]

import datetime

origins = population_grid.copy()
origins.geometry = origins.geometry.centroid

destinations = railway_station.copy()

travel_times = r5py.TravelTimeMatrix(
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
travel_times.head()
```

A {class}`TravelTimeMatrix<r5py.TravelTimeMatrix>` is a child class of
{class}`pandas.DataFrame`. The values in its `travel_time` column are travel
times in minutes between the points identified by `from_id` and `to_id` (the IDs
of the origins and destinations, respectively). As you can see, the `id` value
in the `to_id` column is the same for all rows because our example used only one
destination point (the railway station).


## Save results

If you want to continue analysis later, in a different environment, or simply
retain a clean copy of the results, save the travel time matrix to a CSV file.
Simply use the {meth}`to_csv()<pandas.DataFrame.to_csv()>` method of pandas data
frames:

```{code-cell}
travel_times.to_csv("travel_times_to_helsinki_railway_station.csv")
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
