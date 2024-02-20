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

```{code-cell}
:tags: [remove-input, remove-output]

# this cell is hidden from READTHEDOCS output
# it’s used to
#    - use a different upstream R5 jar, so we can display the
#      geometries of public transport routes, and to

import sys

sys.argv.extend([
    "--r5-classpath",
    "https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-1/r5-v7.1-gp2-2-gd8134d8-all.jar",
])

```

```{code-cell}
:tags: [remove-input, remove-output]

# this cell is hidden in READTHEDOCS
# it loads input geodata for the examples below

# if you opened this notebook elsewhere, be sure to run
# this cell, so data is read from disk

import r5py
import r5py.sampledata.helsinki

transport_network = r5py.TransportNetwork(
    r5py.sampledata.helsinki.osm_pbf,
    [
        r5py.sampledata.helsinki.gtfs,
    ]
)
```

# Advanced use

## Snap origins and destination to the street network

```{code-cell}
:tags: [remove-input]

import folium
import geopandas
import shapely

LONELY_POINT = shapely.Point(24.841466, 60.208892)

geopandas.GeoDataFrame(
    {"id": 1, "geometry": [LONELY_POINT]},
    crs="EPSG:4326",
).explore(
    marker_type="marker",
    map_kwds={
        "center": { "lat": 60.208844, "lng": 24.837684 },
    },
    zoom_start=15,
)
```

Sometimes, origin or destination points are far from the walkable, cyclable, or
drivable street network. Especially when using a regular grid of points, many
origins or destinations of a data set might be in the middle of a swamp (example
above), on top of a mountain, or in the deep forest.

While _r5py_ and _R⁵_ do their best to provide a reasonable route even for these
points, at times, you might want to be able to control the situation a bit
better.

_R5py_’s {class}`TransportNetwork<r5py.TransportNetwork>` allows you to snap a
{class}`GeoSeries<geopandas.GeoSeries>` of {class}`points<shapely.Point>` to
points on the network.

Simply load a transport network, have a geo-data frame with origin or
destination points, and call the transport network’s
{meth}`snap_to_network()<r5py.TransportNetwork.snap_to_network()>` method:

```{code-cell}
import geopandas

origins = geopandas.GeoDataFrame(
    {
        "id": [1, 2],
        "geometry": [
            shapely.Point(24.841466, 60.208892),
            shapely.Point(24.848001, 60.207177),
        ],
    },
    crs="EPSG:4326",
)

origins["snapped_geometry"] = transport_network.snap_to_network(origins["geometry"])

origins
```

```{code-cell}
:tags: [remove-input]

origins["lines"] = origins.apply(
    lambda row: shapely.LineString([row["geometry"], row["snapped_geometry"]]),
    axis=1
)

overview_map = origins.explore(
    marker_type="marker",
    marker_kwds={
        "icon": folium.map.Icon(color="red", icon="ban", prefix="fa"),
    },
    map_kwds={
        "center": {"lat": 60.20910, "lng": 24.84738}
    },
    zoom_start=15,
)
overview_map = origins.set_geometry("snapped_geometry").explore(
    m=overview_map,
    marker_type="marker",
    marker_kwds={
        "icon": folium.map.Icon(color="green", icon="person-walking", prefix="fa"),
    }
)
overview_map = origins.set_geometry("lines").explore(
    m=overview_map,
    zoom_start=15
)

# remove added columns so `origins` is clean for the next cell
origins = origins[["id", "geometry"]].copy()

overview_map
```

By default, snapping takes into consideration all network nodes that support
{class}`TransportMode.WALK<r5py.TransportMode>`, and that are within search
radius of 1600 metres. In other words, points are snapped to the closest path
that is accessible on foot, within a maximum of 1.6 kilometres.

Both parameters can be adjusted. For example, to snap to network nodes
that are drivable, within 500 m, use the following code:

```{code-cell}
origins["snapped_geometry"] = transport_network.snap_to_network(
    origins["geometry"],
    radius=500,
    street_mode=r5py.TransportMode.CAR,
)
origins
```

As you can see, one of the points could not be snapped with the tightened
requirements: it was returned as an ‘empty’ point.

:::{admonition} Convenient short-hands
:class: tip

Both {class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>` and
{class}`DetailedItinerariesComputer<r5py.DetailedItinerariesComputer>` support a
convenient parameter, `snap_to_network`, that controls whether the origins and
destinations should automatically be snapped to the transport network.

```{code}

travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
    ...
    snap_to_network=True,
)
```

:::

## Limit the maximum Java heap size (memory use)

A _Java Virtual Machine_ (JVM) typically restricts the memory usage of programs
it runs. More specifically, the _heap size_ can be limited (see [this
stackoverflow
discussion](https://stackoverflow.com/questions/14763079/what-are-the-xms-and-xmx-parameters-when-starting-jvm)
for a detailed explanation).

The tasks carried out by _R⁵_ under the hood of _r5py_ are fairly
memory-intensive, which is why, by default, _r5py_ allows the JVM to grant up to
80% of total memory to R⁵ (but ensures to always leave at least 2 GiB to the
operating system and other processes).

You may want to lower this limit if you are running other tasks in parallel, or
raise it if you have a dedicated computer with large memory and small
operating system requirements.

To change the memory limit, you can either create a configuration file and set
`max-memory` from there by specifying the `--max-memory` or `-m` command line
arguments, or add the same arguments to `sys.argv`. See detailed explanation on
the [configuration](configuration.md) page.

For instance, to set the maximum heap size to a fixed 12 GiB, you can create a
configuration file in the [location suitable for your operating
system](configuration.md#configuration-via-config-files), and add the following line:

```{code-block} yaml
:name: conf-yml-memory
:caption: ~/.config/r5py.yml

max-memory: 12G
```

## Use a custom installation of R⁵

For some use cases, it can be useful to use a local copy of R⁵, rather than
the one downloaded by _r5py_, for instance, in order to apply custom patches
to extend or modify R⁵’s functionality, or to force the use of a certain
version for longitudinal comparability.

This can be achieved by passing a configuration option or command
line argument to change the class path.

For example, to set a custom classpath inside a Python notebook, you can set
`sys.argv` before importing `r5py`:

```python
import sys
sys.argv.append(["--r5-classpath", "/opt/r5/"])
import r5py
```

To use the patched R⁵ version provided by the [Digital Geography
Lab](https://www.helsinki.fi/en/researchgroups/digital-geography-lab)
on their [GitHub pages](https://github.com/DigitalGeographyLab/r5/releases), for example,
pass the full URL, instead:

```python
import sys
sys.argv.append([
    "--r5-classpath",
    "https://github.com/DigitalGeographyLab/r5/releases/download/v6.9-post16-g1054c1e-20230619/r5-v6.9-post16-g1054c1e-20230619-all.jar"
])
import r5py
```

## Multi-objective routing (Green Paths 2)

:::{admonition} Before starting
:class: info

Before using Multi-objective routing, do familiarize yourself with r5py's
routing components e.g.
{class}`CustomCostTransportNetwork<r5py.CustomCostTransportNetwork>` and
{class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>` in [Quickstart
guide](quickstart.md).

:::

These components provide a possibility to use custom cost weight factors for
segments during routing.  Multi-objective routing means that there is additional
weights - addition to time - for calculating least cost paths during routing.

These custom cost segment weight factors will add additional time `seconds` to
the traversal cost of each segment which is found from the
`custom_cost_segment_weight_factors` dictionary by following formula: `base
traveltime seconds * custom cost segment weight factor * sensitivity`.

These components can be used natively with r5py or via [Green Paths
2.0](https://github.com/DigitalGeographyLab/green-paths-2), which provides
functionality for using Multi-objective routing. It e.g. calculates additional
weight factors for edges supporting various spatial data sources and locations.

In Green Paths 2.0 the multi-objective routing is used to find healthier urban
paths by calculating exposures during active travel, using e.g. greenery, noise
and pollution datasets. The underlying data from which the custom cost weight
factors per road segment are calculated, plays significant role for the accuracy
of weighting segments. See the [Green Paths 2 github
repository](https://github.com/DigitalGeographyLab/green-paths-2) for more.

:::{admonition} Segmenting OSM ways
:class: tip

When using `osm_id` approach for e.g. calculating exposures, the road network
should be split to segments between nodes.  Natively OSM ways expend across
multiple nodes, making exposure calculations using osmid's unaccurat. We do only
want to calculate the exposure of the actual road segments we traversed, not the
entire way, which might extend to various directions. For routing purposes,
using segmented `osm.pbf` network can improve the accuracy of multi-objective
routing. For accurate exposure calculations, segmenting is mandatory.

:::

:::{admonition} Multi-objective routing needs the Green Paths 2.0 patch of R5.
:class: attention

These components are dependant on Green Paths 2.0 patches to the R5 java library.

Green Paths patched source code of R5 can be found from [gp2 branch of Digital
Geography Lab's R5 Github
repository](https://github.com/DigitalGeographyLab/r5/tree/gp2).

Latest version of executable .jar R5 with GP2 patches is hosted in
`releases`/`download`. Easiest is to use the url of .jar which should look
something like this:
[https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-1/r5-v7.1-gp2-2-gd8134d8-all.jar](https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-1/r5-v7.1-gp2-2-gd8134d8-all.jar)

To use custom installation of R5 see: [custom R⁵
jar](advanced-use.md#use-a-custom-installation-of-r⁵)

:::

### CustomCostTransportNetwork

To start using multi-objective routing - which finds routes using additional
weights for segments in addition to travel time - use
{class}`CustomCostTransportNetwork<r5py.CustomCostTransportNetwork>`.  It adds
possibility to define custom edge weights to
`TransportNetwork<r5py.TransportNetwork>`.

The main functionality of CustomCostTransportNetwork is to

1. `Add custom cost segment weights for the routing`
2. `Return list of edge osmids traversed in path`

:::{admonition} Multiple custom cost datas
:class: tip

{class}`CustomCostTransportNetwork<r5py.CustomCostTransportNetwork>` also
supports multiple custom cost datas.  When using multiple custom cost datas you
need to define the parameters as lists and each of the parameter lists needs to
have equal number of elements. When using lists of parameters, the corresponding
name, sensivitity and custom_cost_factors will be paired by their order of
apparence (index). So first elements of each list of name, sensitivity,
custom_cost_factor will makeup 1st set and the second elements will make the 2nd
set and so forth. The approach follows pythons `zip()` principal.

During routing all datasets will be added on top of the edge's base traversal time.

:::

A {class}`CustomCostTransportNetwork<r5py.CustomCostTransportNetwork>` needs the
following input arguments:

- `osm_pbf`: `string` filepath for osm.pbf road network file. Be mindfull of OSM
  way segmenting for accurate results. See [info on Segmenting OSM
  ways](advanced-use.md#multi-objective-routing-green-paths-2)).

- `names`: `string` | `List[string]` name(s) which describes the dataset used
  for the factor calculations.

- `sensitivities`: `float` | `integer` | `List[float | integer]` number used to
  increase the weights of these factors. Increasing or decreasing sensitivity
  you can find different routes with the same factors where the used custom cost
  datas are more or less dominant during routing.

- `custom_cost_segment_weight_factors`: `dictionary[str, float]` |
  `List[dictionary[str, float]]` consisting of osm_id (str) as keys and factor
  (float) as values. The factors should ideally be normalized to e.g. 0.0-1.0
  floats values.
  Using too large values can lead to no routes found if the travel time gets too
  big. Normalizing values across the custom cost data enables coherent and
  comparable values across the network.

- `allow_missing_osmids` `(optional) (experimental)`: `boolean` flag which
  defines if missing osmid's are allowed during routing. Default is True. If
  this is set to False, the routing will fail if there are `ANY` missing osmids
  in the `custom_cost_segment_weight_factors`. Most likely this should be left
  untouched.

### Example use cases for building the network:

:::{admonition} Multiple custom cost datas
:class: tip

"Dataset" referred in this context means a set of parameters having one of each:
`name`, `sensitivity`, `custom_cost_segment_weight_factors`, `(optional)
allow_missing_osmids`.

:::

First initialize OD (origins and destinations) and set to use correct patch (GP2) of R5.

```{code-cell}
# use GP2 patched version of r5

import sys
sys.argv.append([
    "--r5-classpath",
    "https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-1/r5-v7.1-gp2-2-gd8134d8-all.jar"
])

import r5py
import r5py.sampledata.helsinki
```

```{code-cell}
:tags: ["remove-output"]

# init example OD's (origins and destinations)

import geopandas
import shapely
import datetime

population_grid = geopandas.read_file(r5py.sampledata.helsinki.population_grid)

railway_station = geopandas.GeoDataFrame(
    {
        "id": ["railway_station"],
        "geometry": [shapely.Point(24.94152, 60.17066)]
    },
    crs="EPSG:4326",
)

origins = population_grid.copy()
origins.geometry = origins.geometry.centroid

destinations = railway_station.copy()
```

Use `single` custom cost dataset. Defining the paremeters:

```{code-cell}
# populate example segment cost weight factors with some meaningful values
# real dictionary should have .pbf's valid osmids and some meaningfull weight factors
example_data_custom_cost_segment_weights_1 = {
    '122946790': 0.0,
    '28639750': 1.0,
    '57016533': 0.4,
    '122946791': 0.5,
    '57016531': 0.6,
    '255757448': 0.8,
    '122946787': 0.2,
    '255757446': 0.3
}
# you can use your own filepath as the osm.pbf e.g. "/path/to/your/network.osm.pbf"
custom_cost_transport_network_example_1 = r5py.CustomCostTransportNetwork(
    r5py.sampledata.helsinki.osm_pbf,
    "example_1_data_name", 1.2, example_data_custom_cost_segment_weights_1,
)
```

Use `multiple` (two or more) datasets. Instead of defining the parameters, you
need to define lists of parameters.  If you want to use more than two, just add
the parameters to the lists. Notice the importance of element order in lists.
Names with "\_1" and sensitivity 1.1 will create 1 instance of custom costs and
names with "\_2" and sensitivity 1.2 another instance and so forth.

```{code-cell}
# populate example segment cost weight factors with some meaningful values
example_data_custom_cost_segment_weights_2 = {
    '123406154': 1.1,
    '1024048411': 1.2,
    '693578052': 0.55,
    '1024048413': 0.88,
    '35062275': 0.79,
    '693578051': 0.3,
    '1024048412': 0.4,
    '1024048415': 0.7,
    '28639650': 0.2,
    '1024048414': 0.1
}
custom_cost_transport_network_example_2 = r5py.CustomCostTransportNetwork(
    r5py.sampledata.helsinki.osm_pbf,
    ["example_1_data_name", "example_2_data_name"],
    [1.1, 1.2],
    [example_data_custom_cost_segment_weights_1, example_data_custom_cost_segment_weights_2]
)

```

### Routing with CustomCostTransportNetwork

{class}`CustomCostTransportNetwork<r5py.CustomCostTransportNetwork>` can be used
with {class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>` and
{class}`DetailedItinerariesComputer<r5py.DetailedItinerariesComputer>`.

Creating the `routing computers` behave exactly the same as with normal
{class}`TransportNetwork<r5py.TransportNetwork>`. For more information in
routing see Quickstart(quickstart.md) and Detailed
itineraries(detailed-itineraries.md)

:::{admonition} Only Walking and Cycling supported :class: attention

Green Paths 2.0 patch currently only supports active travel modes. Available
{class}`r5py.TransportMode`'s are: `r5py.TransportMode.WALK` and
`r5py.TransportMode.BICYCLE`.

:::

### Example use cases for routing:

Routing with {class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>`

```{code-cell}
# create the travel_time_matrix computer
# using multiple datas
travel_time_matrix_computer_custom_cost_example = r5py.TravelTimeMatrixComputer(
    custom_cost_transport_network_example_2,
    origins=origins,
    destinations=destinations,
    transport_modes=[r5py.TransportMode.WALK],
)

# run the routing
travel_time_matrix_results = travel_time_matrix_computer_custom_cost_example.compute_travel_times()

# see the result `GeoDataFrame`
travel_time_matrix_results.head(5)

```

Routing with {class}`DetailedItinerariesComputer<r5py.DetailedItinerariesComputer>`

```{code-cell}
# create the detailed itineraries computer
detailed_computer_custom_cost_example = r5py.DetailedItinerariesComputer(
    custom_cost_transport_network_example_1,
    origins=origins,
    destinations=destinations,
    transport_modes=[
        r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE
    ],
)

# run the routing for detailed itineraries
detailed_computer_results= detailed_computer_custom_cost_example.compute_travel_details()

# see the result `Geopandas.GeoDataFrame`
detailed_computer_results.head(5)
```

The multi-objective routing does introduce a new return column `osm_ids` which
is a `list` of osmid's from the ways (edge, segment) which were traversed for
each `OD pair`/`Path`. Otherwise the routing results are the same as in
{class}`TravelTimeMatrixComputer<r5py.TravelTimeMatrixComputer>` and
{class}`DetailedItinerariesComputer<r5py.DetailedItinerariesComputer>`.

### Other functionalities

{class}`CustomCostTransportNetwork<r5py.CustomCostTransportNetwork>` also
provides methods for getting `base travel time` and `additional travel times`.
These can be used to see the actual travel time seconds and added seconds for
when R5 uses custom cost factor and sensitivity it adds the seconds to the
travel times which then aren't realistic representations of seconds but more of
a `travel costs`. These methods return `List[Tuple[str, Dict[str, int]]]` where
1st element of tuple is the name of the dataset used and 2nd element dictionary
is osmid, seconds. Each list element represent one custom cost dataset, when not
merged.

Both of these methods support parameters:
`osmids : List[str | int]` and `merged : bool (default=False)`

```{code-cell}
# get the actual (base) travel times
# get all
base_travel_times = custom_cost_transport_network_example_1.get_base_travel_times()
# use print for excessive amounts of ids due to no filtering
print(base_travel_times)
```

```{code-cell}
# get the merged travel times and use a osm_id to filter out unwanted osm_ids
# use some "real" osmids used
base_travel_times_merged_filtered = custom_cost_transport_network_example_1.get_base_travel_times(osmids=[124126960, "124126961"], merged=True)
base_travel_times_merged_filtered
```

```{code-cell}
# use some "real" osmids used
added_cost_seconds = custom_cost_transport_network_example_1.get_custom_cost_additional_travel_times(osmids=[35062275, 1024048413, 123406154])
added_cost_seconds
```

### Further development

The `osm_id` approach is mainly used to support [Green Paths
2](https://github.com/DigitalGeographyLab/green-paths-2) functionality for
routing and combining used segments during routing with exposure values.

For the future development, the `geometry` of segements could also be fetched
with similar logic as the `osm_id`s, making it computationally efficient to get
geometries of paths for e.g. matrices.

Another approach would be to use the current `osm_id`s to get the geometries by
matchin `osm_id`s and getting geometrie that way.

This would be feasible e.g. by

1. converting the `exactly same osm.pbf` file to `Geopandas.GeoDataFrame`.
2. making `osmid the index`.
3. Looping the `osm_id`s and getting each matching rows geometry and building
   `Shapely.MultiLineString` from all the `Shapely.LineString` (and possible
   `Shapely.MultiLineString`).

The Multi-objective routing is meant to be used with `custom cost factors` but
it also can be run with non-empty dictionary and unrelevant placeholder values
for getting the `osm_id`s. This can be beneficial if the ids are meaningfull
somehow or for getting the geometries, like described above.
{class}`DetailedItinerariesComputer<r5py.DetailedItinerariesComputer>` works
great but it isn't meant for excessive amounts of OD pairs and calculations can
become resource intensive and expensive.
