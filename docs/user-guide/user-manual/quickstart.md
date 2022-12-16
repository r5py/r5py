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


# Quickstart

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

### Load transport network

Virtually all operations of `r5py` require a transport network. In this example, we use data from Helsinki metropolitan area, which you can find in the source code repository of r5py in `docs/data/` [(see here)](https://github.com/r5py/r5py/tree/main/docs/data). To import the street and public transport networks, instantiate an `r5py.TransportNetwork` with the file paths to the OSM extract and the GTFS files:

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
   - *Note*: By default, `r5py` summarizes and calculates a median travel time from all possible connections within one hour from given depature time (with 1 minute frequency). It is possible to adjust this time window using `departure_time_window` parameter ([see details here](r5py.RegionalTask)).
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
