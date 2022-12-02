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


# User Manual


## Introduction

**R5py** is a Python library for routing and calculating travel time matrices
on multimodal transport networks (walk, bike, public transport and car).  It
provides a simple and friendly interface to R<sup>5</sup> (*the Rapid Realistic
Routing on Real-world and Reimagined networks*) which is a [routing
engine](https://github.com/conveyal/r5) developed by
[Conveyal](https://conveyal.com/). `R5py` is designed to interact with
[GeoPandas](https://geopandas.org) GeoDataFrames, and it is inspired by
[r5r](https://ipeagit.github.io/r5r) which is a similar wrapper developed for
R. `R5py` exposes some of R5’s functionality via its [Python
API](../reference/reference), in a syntax similar to r5r’s. At the time of this
writing, only the computation of travel time matrices has been fully
implemented. Over time, `r5py` will be expanded to incorporate other
functionalities from R5.


## Data requirements

### Data for creating a routable network

When calculating travel times with `r5py`, you typically need a couple of
datasets:

- **A road network dataset from OpenStreetMap** (OSM) in Protocolbuffer Binary
  (`.pbf`) format:
  - This data is used for finding the fastest routes and calculating the travel
    times based on walking, cycling and driving. In addition, this data is used
for walking/cycling legs between stops when routing with transit.
  - *Hint*: Sometimes you might need modify the OSM data beforehand, e.g., by
    cropping the data or adding special costs for travelling (e.g., for
    considering slope when cycling/walking). When doing this, you should follow
    the instructions on the [Conveyal
    website](https://docs.conveyal.com/prepare-inputs#preparing-the-osm-data).
    For adding customized costs for pedestrian and cycling analyses, see [this
    repository](https://github.com/RSGInc/ladot_analysis_dataprep).

- **A transit schedule dataset** in General Transit Feed Specification
  (GTFS.zip) format (optional):
   - This data contains all the necessary information for calculating travel
     times based on public transport, such as stops, routes, trips and the
     schedules when the vehicles are passing a specific stop. You can read about
     the [GTFS standard here](https://developers.google.com/transit/gtfs/reference).
   - *Hint*: `r5py` can also combine multiple GTFS files, as sometimes you
     might have different GTFS feeds representing, e.g., the bus and metro
     connections.


### Data for origin and destination locations

In addition to OSM and GTFS datasets, you need data that represents the origin
and destination locations (OD-data) for routings. This data is typically stored
in one of the geospatial data formats, such as Shapefile, GeoJSON or
GeoPackage. As `r5py` is built on top of `geopandas`, it is easy to read
OD-data from various different data formats.


### Where to get these datasets?

Here are a few places from where you can download the datasets for creating the routable network:

- **OpenStreetMap data in PBF-format**:

  - [pyrosm](https://pyrosm.readthedocs.io/en/latest/basics.html#protobuf-file-what-is-it-and-how-to-get-one)  library. Allows downloading data directly from Python (based on GeoFabrik and BBBike).
  - [pydriosm](https://pydriosm.readthedocs.io/en/latest/quick-start.html#download-data) library. Allows downloading data directly from Python (based on GeoFabrik and BBBike).
  - [GeoFabrik](http://download.geofabrik.de/) website. Has data extracts for many pre-defined areas (countries, regions, etc).
  - [BBBike](https://download.bbbike.org/osm/bbbike/) website. Has data extracts readily available for many cities across the world. Also supports downloading data by [specifying your own area or interest](https://extract.bbbike.org/).
  - [Protomaps](https://protomaps.com/downloads/osm) website. Allows to download the data with custom extent by specifying your own area of interest.


- **GTFS data**:
  - [Transitfeeds](https://transitfeeds.com/) website. Easy to navigate and find GTFS data for different countries and cities. Includes current and historical GTFS data. Notice: The site will be deprecated in the future.
  - [Mobility Database](https://database.mobilitydata.org) website. Will eventually replace TransitFeeds.
  - [Transitland](https://www.transit.land/operators) website. Find data based on country, operator or feed name. Includes current and historical GTFS data.

### Sample datasets

In the following tutorial, we use various open source datasets:
- The point dataset for Helsinki has been obtained from [Helsinki Region Environmental Services](https://www.hsy.fi/en/environmental-information/open-data/avoin-data---sivut/population-grid-of-helsinki-metropolitan-area/) (HSY) licensed under a Creative Commons By Attribution 4.0.
- The street network for Helsinki is a cropped and filtered extract of OpenStreetMap (© OpenStreetMap contributors, [ODbL license](https://www.openstreetmap.org/copyright))
- The GTFS transport schedule dataset for Helsinki is a cropped and minimised copy of Helsingin seudun liikenne’s (HSL) open dataset ([Creative Commons BY 4.0](https://www.hsl.fi/hsl/avoin-data#aineistojen-kayttoehdot)).
<!-- #endregion -->

## Installation

Before you can start using `r5py`, you need to install it and a few libraries. Check [installation instructions](installation) for more details.


## Configuring `r5py` before using it

It is possible to configure `r5py` in a few different ways (see [configuration instructions](configuration) for details). One of the options that you most likely want to adjust, is **configuring how much memory** (RAM) `r5py` will consume during the calculations. `r5py` runs a powerful Java engine under the hood, and by default it will use **80 % of the available memory** for doing the calculations. However, you can easily adjust this.

If you want to allocate, e.g., a maximum of 5 Gb of RAM for the tool, you can do so by running:

```{code-cell}
import sys
sys.argv.append(["--max-memory", "5G"])
```

By running this, `r5py` will use **at maximum** 5 Gb of memory. However, it does not mean that the tool will necessary use all of this memory if it does not need it.

:::{important}
Notice that changing the amount of allocated memory should alway be done as the first thing in your script, i.e. it should be run **before** importing `r5py`.
:::


## Getting started with `r5py`

Next, we will learn how to calculate travel times with `r5py` between locations spread around the city center area of Helsinki, Finland.

### Load the origin and destination data

Let's start by downloading a sample point dataset into a geopandas `GeoDataFrame` that we can use as our origin and destination locations. For the sake of this exercise, we have prepared a grid of points covering parts of Helsinki. The point data also contains the number of residents of each 250 meter cell:

```{code-cell}
import geopandas

points_url = "https://github.com/r5py/r5py/raw/main/docs/data/Helsinki/population_points_2020.gpkg"
points = geopandas.read_file(points_url)
points.head()
```

The `points` GeoDataFrame contains a few columns, namely `id`, `population` and `geometry`. The `id` column with unique values and `geometry` columns are required for `r5py` to work. If your input point dataset does not have an `id` column with unique values, `r5py` will throw an error.

To get a better sense of the data, let's create a map that shows the locations of the points and visualise the number of people living in each cell (the cells are represented by their centre point):

```{code-cell}
points.explore("population", cmap="Reds", marker_kwds={"radius": 12})
```

Let's pick one of these points to represent our **origin** and store it in a separate GeoDataFrame:

```{code-cell}
origin = points.loc[points["id"] == 54].copy()
origin.explore(color="blue", max_zoom=14, marker_kwds={"radius": 12})
```

<!-- #region tags=[] -->
### Load transport network

Virtually all operations of `r5py` require a transport network. In this example, we use data from Helsinki metropolitan area, which you can find in the source code repository of r5py in `docs/data/` [(see here)](https://github.com/r5py/r5py/tree/main/docs/data). To import the street and public transport networks, instantiate an `r5py.TransportNetwork` with the file paths to the OSM extract and the GTFS files:
<!-- #endregion -->

```{code-cell}
:tags: ["remove-input", "remove-output"]

# this cell is hidden from output
# it’s used to set sys.path to point to the local repo
import pathlib
import sys

NOTEBOOK_DIRECTORY = pathlib.Path().resolve()
DATA_DIRECTORY = NOTEBOOK_DIRECTORY.parent / "_static" / "data"
R5PY_DIRECTORY = NOTEBOOK_DIRECTORY.parent.parent / "src"
sys.path.insert(0, str(R5PY_DIRECTORY))
```

```{code-cell}
from r5py import TransportNetwork

transport_network = TransportNetwork(
    f"{DATA_DIRECTORY}/Helsinki/kantakaupunki.osm.pbf",
    [
        f"{DATA_DIRECTORY}/Helsinki/GTFS.zip"
    ]
)
```

At this stage, `r5py` has created the routable transport network and it is stored in the `transport_network` variable. We can now start using this network for doing the travel time calculations.


### Compute travel time matrix from one to all locations

A travel time matrix is a dataset detailing the travel costs (e.g., time) between given locations (origins and destinations) in a study area. To compute a travel time matrix with `r5py` based on public transportation, we first need to initialize an `r5py.TravelTimeMatrixComputer` object. As inputs, we pass following arguments for the `TravelTimeMatrixComputer`:
- `transport_network`, which we created in the previous step representing the routable transport network.
- `origins`, which is a GeoDataFrame with one location that we created earlier (however, you can also use multiple locations as origins).
- `destinations`, which is a GeoDataFrame representing the destinations (in our case, the `points` GeoDataFrame).
- `departure`, which should be Python's `datetime` object (in our case standing for "22nd of February 2022 at 08:30") to tell `r5py` that the schedules of this specific time and day should be used for doing the calculations.
   - *Note*: By default, `r5py` summarizes and calculates a median travel time from all possible connections within one hour from given depature time (with 1 minute frequency). It is possible to adjust this time window using `departure_time_window` parameter ([see details here](../reference/reference.html#r5py.RegionalTask)).
- `transport_modes`, which determines the travel modes that will be used in the calculations. These can be passed using the options from the `TransitMode` and `LegMode` classes.
  - *Hint*: To see all available options, run `help(TransitMode)` or `help(LegMode)`.

:::{note} In addition to these ones, the constructor also accepts many other parameters [listed here](https://r5py.readthedocs.io/en/stable/reference.html#r5py.RegionalTask), such as walking and cycling speed, maximum trip duration, maximum number of transit connections used during the trip, etc.
:::

Now, we will first create a `travel_time_matrix_computer` instance as described above:

```{code-cell}
import datetime
from r5py import TravelTimeMatrixComputer, TransitMode, LegMode


travel_time_matrix_computer = TravelTimeMatrixComputer(
    transport_network,
    origins=origin,
    destinations=points,
    departure=datetime.datetime(2022,2,22,8,30),
    transport_modes=[TransitMode.TRANSIT, LegMode.WALK]
)

```

Running this initializes the `TravelTimeMatrixComputer`, but any calculations were not done yet.
To actually run the computations, we need to call `.compute_travel_times()` on the instance, which will calculate the travel times between all points:

```{code-cell}
travel_time_matrix = travel_time_matrix_computer.compute_travel_times()
travel_time_matrix.head()
```

As a result, this returns a `pandas.DataFrame` which we stored in the `travel_time_matrix` variable. The values in the `travel_time` column are travel times in minutes between the points identified by `from_id` and `to_id`. As you can see, the `id` value in the `from_id` column is the same for all rows because we only used one origin location as input.

To get a better sense of the results, let's create a travel time map based on our results. We can do this easily by making a table join between the `points` GeoDataFrame and the `travel_time_matrix`. The key in the `travel_time_matrix` table is the column `to_id` and the corresponding key in `points` GeoDataFrame is the column `id`:

```{code-cell}
join = points.merge(travel_time_matrix, left_on="id", right_on="to_id")
join.head()
```

Now we have the travel times attached to each point, and we can easily visualize them on a map:

```{code-cell}
join.explore("travel_time", cmap="Greens", marker_kwds={"radius": 12})
```

### Compute travel time matrix from all to all locations

Running the calculations between all points in our sample dataset can be done in a similar manner as calculating the travel times from one origin to all destinations.
Since, calculating these kind of all-to-all travel time matrices is quite typical when doing accessibility analyses, it is actually possible to calculate a cross-product between all points just by using the `origins` parameter (i.e. without needing to specify a separate set for destinations). `r5py` will use the same points as destinations and produce a full set of origins and destinations:


```{code-cell}
travel_time_matrix_computer = TravelTimeMatrixComputer(
    transport_network,
    origins=points,
    departure=datetime.datetime(2022,2,22,8,30),
    transport_modes=[TransitMode.TRANSIT, LegMode.WALK]
)
travel_time_matrix_all = travel_time_matrix_computer.compute_travel_times()
travel_time_matrix_all.head()
```

```{code-cell}
travel_time_matrix_all.tail()
```

```{code-cell}
len(travel_time_matrix_all)
```

As we can see from the outputs above, now we have calculated travel times between all points (n=92) in the study area. Hence, the resulting DataFrame has almost 8500 rows (92x92=8464). Based on these results, we can for example calculate the median travel time to or from a certain point, which gives a good estimate of the overall accessibility of the location in relation to other points:

```{code-cell} tags=[]
median_times = travel_time_matrix_all.groupby("from_id")["travel_time"].median()
median_times
```

To estimate, how long does it take in general to travel between locations in our study area (i.e. what is the baseline accessibility in the area), we can calculate the mean (or median) of the median travel times showing that it is approximately 22 minutes:

```{code-cell}
median_times.mean()
```

Naturally, we can also visualize these values on a map:

```{code-cell}
overall_access = points.merge(median_times.reset_index(), left_on="id", right_on="from_id")
overall_access.head()
```

```{code-cell}
overall_access.explore("travel_time", cmap="Blues", scheme="natural_breaks", k=4, marker_kwds={"radius": 12})
```

In our study area, there seems to be a bit poorer accessibility in the Southern areas and on the edges of the region (i.e. we witness a classic edge-effect here).


## Advanced usage

### Compute travel times with a detailed breakdown of the routing results


In case you are interested in more detailed routing results, you can use a `DetailedItinerariesComputer` instead of the `TravelTimeMatrixComputer`. This will provide roughly the same information as in the previous examples, but it also brings more detailed information about the routes. `DetailedItinerariesComputer` produces information about the used routes for each origin-destination pair, as well as total time disaggregated by access, waiting, in-vehicle and transfer times:

```{code-cell}
from r5py import DetailedItinerariesComputer

detailed_itineraries_computer = DetailedItinerariesComputer(
    transport_network,
    origins=origin,
    destinations=points,
    departure=datetime.datetime(2022,2,22,8,30),
    transport_modes=[TransitMode.TRANSIT, LegMode.WALK],
)
travel_time_matrix_detailed = detailed_itineraries_computer.compute_travel_times()
travel_time_matrix_detailed.head()
```

As you can see, the result contains much more information than earlier, see the following table for explanations:

| Column        | Description                                                          | Data type |
| ------------- | -------------------------------------------------------------------- | --------- |
| **routes**        | The route-ids (lines) used during the trip                           | list      |
| **board_stops**   | The stop-ids of the boarding stops                                   | list      |
| **alight_stops**  | The stop-ids of the alighting stops                                  | list      |
| **ride_times**    | In vehicle ride times of individual journey legs                     | list      |
| **access_time**   | The time it takes for the "first mile" of a trip                     | float     |
| **egress_time**   | The time it takes for the "last mile" of a trip                      | float     |
| **transfer_time** | The time it takes to transfer from vechile to another                | float     |
| **wait_times**    | The time(s) it take to wait for the vehicle at a stop                | list      |
| **total_time**    | Sum(ride_times, access_time, egress_time, transfer_time, wait_times) | float     |
| **n_iterations**  | Number of iterations used for calculating the travel times           | int       |



### Compute travel times for different percentiles

Because `r5py` calculates travel times for all possible transit departure possibilities within an hour (with one minute frequency), we basically get a distribution of travel times. It is possible to gather and return information about the travel times at different percentiles of this distribution based on all computed trips (sorted from the fastest to slowest connections). By default, the returned time in `r5py` is the median travel time (i.e. `50`). You can access these percentiles by using a parameter `percentiles` which accepts a list of integers representing different percentiles, such as `[25, 50, 75]` which returns the travel times at those percentiles:

```{code-cell}
travel_time_matrix_computer = TravelTimeMatrixComputer(
    transport_network,
    origins=origin,
    destinations=points,
    departure=datetime.datetime(2022,2,22,8,30),
    transport_modes=[TransitMode.TRANSIT, LegMode.WALK],
    percentiles=[25, 50, 75],
)
travel_time_matrix_detailed = travel_time_matrix_computer.compute_travel_times()
travel_time_matrix_detailed.head()
```
