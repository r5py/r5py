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
