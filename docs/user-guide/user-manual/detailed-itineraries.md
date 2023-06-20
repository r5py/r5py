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

# TODO:
# - a lot
# - specifically, do not forget to mention the following things:
#   - if R5’s TransitLayer is compiled with SAVE_SHAPES=false (the default),
#     geometries for PT routing are straight lines between stops; distances are
#     based on these geometries and, consequently, shortened


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

# also this cell is hidden in READTHEDOCS
# it loads input geodata for the examples below

# if you opened this notebook elsewhere, be sure to run
# this cell, so data is read from disk

import geopandas
import r5py
import shapely

population_grid = geopandas.read_file(DATA_DIRECTORY / "Helsinki" / "population_grid_2020.gpkg")
RAILWAY_STATION = shapely.Point(24.941521, 60.170666)

transport_network = r5py.TransportNetwork(
    f"{DATA_DIRECTORY}/Helsinki/kantakaupunki.osm.pbf",
    [
        f"{DATA_DIRECTORY}/Helsinki/GTFS.zip",
    ]
)
```

# Compute travel times with a detailed breakdown of the routing results

In case you are interested in more detailed routing results, you can use
`DetailedItinerariesComputer`. In contrast to `TravelTimeMatrixComputer`, it
reports individual trip segments, and possibly multiple options for each trip. 

As such, `DetailedItinerariesComputer`’s output is structured in a different
way, too. It provides one row per trip segment, multiple trip segments together
constitute a trip option, of which there might be several per `from_id`/`to_id`
pair. The results also include information on the public transport routes (e.g.,
bus line numbers) used on the trip, as well as a {class}`shapely.geometry` for
each segment.


```{code-cell}
:tags: ["remove-output"]

import datetime
import r5py

origins = population_grid.sample(10).copy()
origins.geometry = origins.geometry.centroid

destinations = geopandas.GeoDataFrame(
        {
            "id": [1],
            "geometry": [RAILWAY_STATION]
        },
        crs="EPSG:4326",
)

detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
    transport_network,
    origins=origins,
    destinations=destinations,
    departure=datetime.datetime(2022,2,22,8,30),
    transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
)
```

```{code-cell}
travel_time_matrix_detailed = detailed_itineraries_computer.compute_travel_details()
travel_time_matrix_detailed.head()
```


As you can see, the result contains much more information than earlier, see the
following table for explanations:

% TODO: update columns

`routes` ({class}`list`)
: The public transport lines (route IDs in the GTFS data set) used during the
trip

`board_stops` ({class}`list`)
: The public transport stops (stop IDs) at which a vehicle is boarded, in
sequential order

`alight_stops` ({class}`list`)
: The public transport stops (stop IDs) at which a vehicle is disembarked, in
sequential order

`ride_times` ({class}`list`[{class}`float`])
: The ride times of individual journey legs (on each vehicle), in sequential
order

`access_time` ({class}`float`)
: The time to reach the first public transport stop (with
{class}`access_modes<r5py.RegionalTask>`, default
{class}`r5py.TransportMode.WALK<r5py.TransportMode>`): the ‘first mile’

`egress_time` ({class}`float`)
: The time from the last public transport stop (with
{class}`egress_modes<r5py.RegionalTask>`, default
{class}`r5py.TransportMode.WALK<r5py.TransportMode>`): the ‘last mile’

`transfer_time` ({class}`float`)
: The total time spent transfering from one vehicle to another (e.g., walking
between platforms)

`wait_times` ({class}`list`[{class}`float`])
: The waiting times for a vehicle at each public transport stop, in sequential
order

`total_time` ({class}`float`)
: The total time to reach the destination, the sum of `ride_times`,
`access_time`, `egress_time`, `transfer_time`, and `wait_times`

`n_iterations` ({class}`int`)
: The results (other columns, see above) are based on `n_iterations` possible
routes within {class}`departure_time_window<r5py.DetailedItinerariesComputer>`,
summarised using {class}`breakdown_stat<r5py.DetailedItinerariesComputer>`
(default: {class}`r5py.BreakdownStat.MEAN<r5py.BreakdownStat>`)
