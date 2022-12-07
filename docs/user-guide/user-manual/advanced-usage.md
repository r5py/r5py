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


# Advanced Usage

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


```{code-cell}
import geopandas

points_url = "https://github.com/r5py/r5py/raw/main/docs/data/Helsinki/population_points_2020.gpkg"
points = geopandas.read_file(points_url)
```

```{code-cell}
origin = points.loc[points["id"] == 54].copy()
origin.explore(color="blue", max_zoom=14, marker_kwds={"radius": 12})
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

## Compute travel times with a detailed breakdown of the routing results


In case you are interested in more detailed routing results, you can use a `DetailedItinerariesComputer` instead of the `TravelTimeMatrixComputer`. This will provide roughly the same information as in the previous examples, but it also brings more detailed information about the routes. `DetailedItinerariesComputer` produces information about the used routes for each origin-destination pair, as well as total time disaggregated by access, waiting, in-vehicle and transfer times:

```{code-cell}
from r5py import DetailedItinerariesComputer, TransitMode, LegMode
import datetime

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



## Compute travel times for different percentiles

Because `r5py` calculates travel times for all possible transit departure possibilities within an hour (with one minute frequency), we basically get a distribution of travel times. It is possible to gather and return information about the travel times at different percentiles of this distribution based on all computed trips (sorted from the fastest to slowest connections). By default, the returned time in `r5py` is the median travel time (i.e. `50`). You can access these percentiles by using a parameter `percentiles` which accepts a list of integers representing different percentiles, such as `[25, 50, 75]` which returns the travel times at those percentiles:

```{code-cell}
from r5py import TravelTimeMatrixComputer

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
