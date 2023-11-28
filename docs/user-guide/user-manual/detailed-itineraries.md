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


# Compute travel times with a detailed breakdown of the routing results

## Detailed itineraries

In case you are interested in more detailed routing results, you can use
{class}`DetailedItinerariesComputer<r5py.DetailedItinerariesComputer>`. In
contrast to {class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>`, it
reports individual trip segments, and possibly multiple alternative routes for
each trip.

As such,
{class}`DetailedItinerariesComputer<r5py.DetailedItinerariesComputer>`’s output
is structured in a different way, too. It provides one row per trip segment,
multiple trip segments together constitute a trip option, of which there might
be several per `from_id`/`to_id` pair. The results also include information on
the public transport routes (e.g., bus line numbers) used on the trip, as well
as a {class}`shapely.geometry` for each segment.

:::{admonition} Detailed itineraries are computationally expensive
:class: attention

Computing detailed itineraries is significantly more time-consuming than
calculating simple travel times. As such, think twice whether you actually need
the detailed information output from this function, and how you might be able to
limit the number of origins and destinations you need to compute.

For the examples below, to reduce computation effort, we use a sample of 3
origin points and one single destination (the railway station) in our sample
data of Helsinki.

:::


```{code-cell}
:tags: [remove-output]

import geopandas
import r5py
import r5py.sampledata.helsinki
import shapely

population_grid = geopandas.read_file(r5py.sampledata.helsinki.population_grid)
RAILWAY_STATION = shapely.Point(24.941521, 60.170666)

transport_network = r5py.TransportNetwork(
    r5py.sampledata.helsinki.osm_pbf,
    [
        r5py.sampledata.helsinki.gtfs,
    ]
)
```


```{code-cell}
:tags: ["remove-output"]

import datetime
import r5py

origins = population_grid.sample(3).copy()
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
    snap_to_network=True,
)
```

:::{admonition} Snap to network
:class: info

If you read the code block above especially carefully, you may have noticed that
we added an option `snap_to_network=True` to
{class}`DetailedItinerariesComputer<r5py.DetailedItinerariesComputer>`. This
option does exactly what it says on the outside: it attempts to snap all origin
and destination points to the transport network before routing. This can help
with points that come to lie in an otherwise inaccessible area, such as a fenced
area, a swamp, or the middle of a lake.

For a detailed description of the functionality, see the [Advanced
use](advanced-use.md#snap-origins-and-destination-to-the-street-network) page.

:::


```{code-cell}
travel_details = detailed_itineraries_computer.compute_travel_details()
travel_details
```


As you can see, the result contains much more information than earlier.
Depending on your screen size, you might even have to scroll further right to
see all columns.

Especially in the case of public transport routes, or when choosing a list of
different {attr}`transport_modes<r5py.RegionalTask.transport_modes>`, also the
table structure of the results is more complex: For each origin/destination
pair, one or more possible `option` is reported, which in turn can consist of
one or more `segment`s. Both options and segments are numbered sequentially,
starting at `0`.

Each segment, then, represents one row in the results table, and provides
information about the transport mode used for a segment, time travelled,
possible wait time (before the departure of a public transport vehicle), the
route (e.g., bus number, metro line), and finally a line geometry representing
the travelled path.

See the following table for a complete list of columns returned by
{meth}`DetailedItinerariesComputer.compute_travel_details()<r5py.DetailedItinerariesComputer.compute_travel_details()>`:


`from_id` (same type as `origins["id"]`)
: the origin of the trip this segment belongs to

`to_id` (same type as `destinations["id"]`)
: the destination of the trip this segment belongs to

`option` ({class}`int`)
: sequential number enumerating the the different trip options found. Each trip
option consists of one or more trip segments. (starts with `0`)

`segment` ({class}`int`)
: sequential number enumerating the segments the current trip option consists
of. (starts with `0`)

`transport_mode` ({class}`r5py.TransportMode`)
: the transport mode used on the current segment

`departure_time` ({class}`datetime.datetime`)
: the departure date and time of the public transport vehicle used for the
current segment; `NaT` in case of other modes of transport

`distance` ({class}`float`)
: the distance travelled on the current segment, in metres. For public
transport, see [note below](detailed-geometries-with-upstream-r5).

`travel_time` ({class}`datetime.timedelta`)
: The time spent travelling on the current segment

`wait_time` ({class}`datetime.timedelta`)
: if the current segment is a public transport vehicle: wait time between the
arrival of the previous trip segment and the departure of the current segment.

`route` ({class}`str`)
: if the current segment is a public transport vehicle: the route number (or
other id), as specified in the input GTFS data set, e.g. bus numbers, metro line
names

`geometry` ({class}`shapely.LineString`)
: the path travelled on the current segment. For public transport, see [note
below](detailed-geometries-with-upstream-r5).


(detailed-geometries-with-upstream-r5)=

:::{admonition} Geometries of public transport routes, and distances travelled
:class: important

The default upstream version of R⁵ is compiled with
`com.conveyal.r5.transit.TransitLayer.SAVE_SHAPES = false`, which improves
performance by *not reading the geometries included in GTFS data sets*.

As a consequence, the `geometry` reported by
{class}`DetailedItinerariesComputer<r5py.DetailedItinerariesComputer>` are
straight lines in-between the stops of a public transport line, and do not
reflect the actual path travelled in public transport modes.

With this in mind, *r5py* does not attempt to compute the distance of public
transport segments if `SAVE_SHAPES = false`, as distances would be very crude
approximations, only. Instead it reports `NaN`/`None`.

R⁵py ships with a version of R⁵ that has been patched to retain geometries.
Unless you use a [custom R⁵
jar](advanced-use.md#use-a-custom-installation-of-r⁵), you should not be
bothered by this.
:::


## Visualise travel details

It’s not difficult to plot the detailed routes in a map, however, a couple more
steps are needed than with simple travel times.
{meth}`GeoDataFrame.explore()<geopandas.GeoDataFrame.explore()>` cannot handle
the column types {class}`r5py.TransportMode` and {class}`datetime.timedelta` -
the conversion is quick and easy, though:

```{code-cell}
travel_details["mode"] = travel_details.transport_mode.astype(str)
travel_details["travel time (min)"] = travel_details.travel_time.apply(
    lambda t: round(t.total_seconds() / 60.0, 2)
)
travel_details["trip"] = travel_details.apply(
    lambda row: f"{row.from_id} → railway station",
    axis=1
)

detailed_routes_map = (
    travel_details[
        [
            "geometry",
            "distance",
            "mode",
            "travel time (min)",
            "from_id",
            "to_id",
            "trip",
            "option",
            "segment",
        ]
    ]
    .explore(
        tooltip=["trip", "option", "segment", "mode", "travel time (min)", "distance"],
        column="mode",
        tiles="CartoDB.Positron",
    )
)
```

Let’s also add the origins and the destination to the map:

```{code-cell}
import folium
import folium.plugins
import pandas

folium.Marker(
    (RAILWAY_STATION.y, RAILWAY_STATION.x),
    icon=folium.Icon(
        color="green",
        icon="train",
        prefix="fa",
    )
).add_to(detailed_routes_map)

points = geopandas.GeoDataFrame(
    pandas.DataFrame(
        {"id": detailed_itineraries_computer.od_pairs["id_origin"].unique()}
    )
    .set_index("id")
    .join(population_grid.set_index("id"))
    .reset_index()
)
points.geometry = points.geometry.to_crs("EPSG:3875").centroid.to_crs("EPSG:4326")

points.apply(
    lambda row: (
        folium.Marker(
            (row["geometry"].y, row["geometry"].x),
            icon=folium.plugins.BeautifyIcon(
                icon_shape="marker",
                number=row["id"],
                border_color="#728224",
                text_color="#728224",
            ),
        ).add_to(detailed_routes_map)
    ),
    axis=1,
)

detailed_routes_map
```


## Export the detailed routes

If you want to further analyse the resulting routes, for instance, in a desktop
{abbr}`GIS (geoinformation system)`, you can export the
{class}`GeoDataFrame<geopandas.GeoDataFrame>` to a [wide range of file
formats](https://geopandas.org/en/stable/docs/user_guide/io.html#writing-spatial-data),
using the {meth}`to_file()<geopandas.GeoDataFrame.to_file()>` method.

Note that many geospatial file formats do not support
{class}`datetime.timedelta` columns, or columns with custom objects, such as the
{class}`r5py.TransportMode` data. Similar to the above example, with a few
simple steps we can convert the values accordingly:

```{code-cell}
travel_details["transport_mode"] = travel_details.transport_mode.astype(str)
travel_details["travel time (min)"] = travel_details.travel_time.apply(
    lambda t: round(t.total_seconds() / 60.0, 2)
)
travel_details["wait time (min)"] = travel_details.wait_time.apply(
    lambda t: round(t.total_seconds() / 60.0, 2)
)

# keep all columns except travel time and wait time (which we renamed to
# reflect the unit of measurement)
travel_details = travel_details[
    [
        "from_id",
        "to_id",
        "option",
        "segment",
        "transport_mode",
        "departure_time",
        "distance",
        "travel time (min)",
        "wait time (min)",
        "route",
        "geometry",
    ]
]

travel_details.to_file("detailed_itineraries.gpkg")

```
