---
jupytext:
  formats: md:myst
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

# Travel-time matrices

```{code-cell}
:tags: [remove-input, remove-output]

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
:tags: [remove-input, remove-output]

# also this cell is hidden from READTHEDOCS output
# it’s used to set a stricter memory limit in binderhub notebooks
# as otherwise, the examples would fail

import os

if "MEM_LIMIT" in os.environ:  # binder/kubernetes!
    max_memory = int(os.environ["MEM_LIMIT"]) / 2
    sys.argv.extend(["--max-memory", f"{max_memory}"])
```

:::{dropdown} What is a travel time matrix?
:open:
:color: light
:margin: 1 5 0 0

A travel time matrix is a table that shows the travel time between all pairs of
a set of locations in an urban area. The locations represent typical origins and
destinations, such as everyday services and residential homes, or are a complete
set of locations covering the entire area wall-to-wall, such as census polygons
or a regular grid.

A travel time matrix is a key piece of information in transportation research
and planning. It allows us to study how easily people can reach different
destinations, to evaluate the impacts of transport and land use policies, to
analyse accessibility patterns and to examine how accessibility is influenced by
factors such as the quality of public transport systems, street networks, and
land use patterns. Travel time matrices can also be used to identify in which
areas and for which groups of people a city works best and worst. Altogether,
this makes travel time matrices a critical information to help cities become
more equitable and more sustainable, and to foster a good quality of life for
their residents.

Successful recent research that either used or produced travel time matrices
include the work of the Digital Geography Lab at the University of Helsinki
(e.g., {cite:t}`tenkanen_longitudinal_2020`, {cite:t}`salonen_modelling_2013`,
or {cite:t}`jarv_dynamic_2018`), the Mobility Network at the University of
Toronto (e.g., {cite:t}`farber_dynamic_pt_2017`,
{cite:t}`farber_temporal_variablity_2014`), and the Access to Opportunities
Project (AOP) at the Institute for Applied Economic Research - IPEA (e.g.,
{cite:t}`pereira_geographic_2021`, {cite:t}`braga_evaluating_2023`,
{cite:t}`herszenhut_impact_2022`).
:::


## Load a transport network

As briefly visited in [Quickstart](quickstart) and dicussed in detail in [Data
Requirements](data-requirements), fundamentally, two types of input data are
required for computing a travel time matrix:

- a transport network, and
- a set of origins and destinations

In the example below, we first create a
{class}`TransportNetwork<r5py.TransportNetwork>`. To do so, we load an
OpenStreetMap extract of the São Paulo city centre as well as a public transport
schedule in GTFS format covering the same area:

```{code-cell}
:tags: [remove-output]

import r5py

transport_network = r5py.TransportNetwork(
    DATA_DIRECTORY / "São Paulo" / "spo_osm.pbf",
    [
        DATA_DIRECTORY / "São Paulo" / "spo_gtfs.zip",
    ]
)
```

Studies that compare accessibility between different neighbourhoods tend to use
a regular grid of points that covers the study area as origins or destinations.
Recently, hexagonal grids, such as Uber’s [H3 indexing
system](https://h3geo.org/) have gained popularity, as they assure equidistant
neighbourhood relationships (all neighbouring grid cells’ centroids are at the
same distance; in a grid of squares, the diagonal neighbours are roughly 41%
further than the horizontal and vertical ones).

We prepared such a hexagonal grid for São Paulo, and added the counts of
`population`, `jobs`, and `schools` within each cell as separate columns.
The `id` column refers to the H3 address of the grid cells.

```{code-cell}
import geopandas

hexagon_grid = geopandas.read_file(DATA_DIRECTORY / "São Paulo" / "spo_hexgrid_EPSG32723.gpkg.zip")
hexagon_grid
```

We can use {meth}`explore()<geopandas.GeoDataFrame.explore()>` to plot the
hexagonal grid in a map:

```{code-cell}
hexagon_grid.explore()
```

*R5py* expects origins and destinations to be point geometries. For grid cells,
the geometric center point (‘centroid’) is a good approximisation. One can use
{attr}`geopandas.GeoDataSeries.centroid` to quickly derive a centroid (point)
geometry from a polygon. We will create one data frame for origins, and one for
destinations:

```{code-cell}
origins = hexagon_grid.copy()
origins["geometry"] = origins.geometry.centroid
```

```{code-cell}
destinations = hexagon_grid.copy()
destinations["geometry"] = destinations.geometry.centroid
```


## Compute a travel time matrix

With this, we have all input data sets needed for computing a travel time
matrix: a transport network, origins, and destinations. We still need to decide
which modes of transport should be used, and the departure time in our analysis.

The modes of transport can be passed as a list of different
{class}`r5py.TransportMode`s (or their {class}`str` equivalent). Meanwhile, the
departure must be a {class}`datetime.datetime`. If you search for public
transport routes, [double-check that the departure date and time is covered by
the input GTFS data set](check-gtfs-files).

```{code-cell}
import datetime

travel_time_matrix = r5py.TravelTimeMatrixComputer(
    transport_network,
    origins=origins,
    destinations=destinations,
    transport_modes=[r5py.TransportMode.TRANSIT],
    departure=datetime.datetime(2019, 5, 13, 14, 0, 0),
).compute_travel_times()
```

The output of
{meth}`compute_travel_times()<r5py.TravelTimeMatrixComputer.compute_travel_times()>`
is a table in which each row describes the travel time (`travel_time`) from an
origin (`from_id`), to a destination (`to_id`).

```{code-cell}
travel_time_matrix
```

```{code-cell}
:tags: [remove-output, remove-input]

import myst_nb

origins_length = len(origins)
destinations_length = len(destinations)
matrix_length = origins_length * destinations_length

myst_nb.glue("origins_length", origins_length, display=False)
myst_nb.glue("destinations_length", destinations_length, display=False)
myst_nb.glue("matrix_length", matrix_length, display=False)
```

:::{dropdown} A note about transit travel times and travel time windows
:open:
:color: light
:margin: 1 5 0 0

With transit travel times, individuals can face (sometimes significantly)
different total travel times depending on when they start their journey. For
example, a rider taking a bus that comes every 15 minutes on the 15-minute mark
will face a travel time that is 14 minutes longer if they arrive at the stop at
09:01 versus if they arrive at 09:15.

To account for that, the R5 engine computes a travel time for every minute in a
specified interval, and reports a median (or, with some customization a
percentile other than the median) travel time over that intervale. For example,
if the specified window is 60 minutes long and the `departure` parameter is set
to 09:00, then the reported travel time will be the median of the 60
minute-by-minute travel times between 09:00 and 10:00.

In r5py the default `departure_time_window` (the interval over which to sample)
is set to 10 minutes. This is done to allow for a result that is as close as
possible to a "single" travel time measure.

**Be careful** as choosing very low intervals (or even not-very-low) intervals
can have some adverse effects on the ability of R5 to find a route to a
destination. If you are working with transit schedules that have very low
frequencies (large gaps in time between subsequent vehicles), you may want to
ensure that `departure_time_window` is set significantly higher than these
headway gaps. The reasons for this are quite technical, but you can read more if
you are interested in the discussion on this issue by visiting [this GitHub
issue](https://github.com/r5py/r5py/issues/292).
:::

The {class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>` creates an
all-to-all matrix in long format. In other words, the results contain one row
for every combination of origins and destinations. Since we have
{glue:}`origins_length` origins and {glue:}`destinations_length` destinations,
the output travel time matrix is {glue:}`matrix_length` rows long.

Alternatively, and possibly more intuitively, we can display the travel time
matrix table as a matrix in wide format, using {meth}`pandas.DataFrame.pivot()`:

```{code-cell}
travel_time_matrix.pivot(index="from_id", columns="to_id", values="travel_time")
```

***


## Explore results

### Travel times from anywhere to a particular place

Once the travel time matrix is computed, we can use the data to analyse and
visualise different measures of accessibility. For instance, we can filter the
table to show all rows for which the destination is the [Praça da
Sé](https://en.wikipedia.org/wiki/Pra%C3%A7a_da_S%C3%A9), a public square in the
centre of the city. By plotting the travel times in a map, we can quickly assess
how long it takes for residents from different parts of the city to reach this
square by public transport.

For this we first create a copy of the result data frame, filtered to contain
only rows with `to_id` referencing the Praça da Sé. Then, we join this table to
the input hexagonal grid, and drop any records that have `NaN` values, i.e., for
which there was no result. Finally, as we did above, we use the
{meth}`explore()<geopandas.GeoDataFrame.explore()>` to display the values in a
map.

```{code-cell}
PRAÇA_DA_SÉ = "89a8100c02fffff"

travel_times_to_centre = travel_time_matrix[travel_time_matrix["to_id"] == PRAÇA_DA_SÉ].copy()
travel_times_to_centre = travel_times_to_centre.set_index("from_id")[["travel_time"]]

hexagons_with_travel_time_to_centre = (
    hexagon_grid.set_index("id").join(travel_times_to_centre)
)

hexagons_with_travel_time_to_centre
```

```{code-cell}
hexagons_with_travel_time_to_centre.explore(
    column="travel_time",
    cmap="YlOrBr",
    tiles="CartoDB.Positron",
)
```

You can clearly see how travel times do not increase uniformly, but are shorter
along the major transport axis (metro, railways, bus corridors).


***


### Aggregated/average accessibility

Another quick way of getting an understanding of how well different parts of the
city are served by public transport is to aggregate the travel times from or to
each cell over the entire study region. Of course, this creates [edge
effects](https://doi.org/10.1016/B978-008044910-4.00423-5), so in our limited
example, grid cells further outside will have worse over-all accessibility
values. However, if an entire city region, e.g., covering the entire public
transport network, can be captured in one analysis, unwanted artefacts of the
analysis have a smaller impact.

To aggregate travel times, we can use the
{meth}`groupby()<pandas.DataFrame.groupby()>` method of pandas’ data frames, and
one of the different aggregation functions available for the resulting
{class}`pandas.GroupBy` objects. For instance, to show the median travel time
from any cell to any other cell in our grid, we group the results using
`from_id` and {meth}`median()<pandas.GroupBy.median()>`:

```{code-cell}
median_travel_times = travel_time_matrix.groupby("from_id").median("travel_time")
median_travel_times
```

Again, we can join these median travel times to the hexagonal grid to display a
nice map:

```{code-cell}
hexagons_with_median_travel_times = (
    hexagon_grid.set_index("id").join(median_travel_times)
)

hexagons_with_median_travel_times.explore(
    column="travel_time", 
    cmap="YlOrBr",
    tiles="CartoDB.Positron",
)
```

## Bibliography

:::{bibliography}
:filter: docname in docnames
:::
