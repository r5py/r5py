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

```{code-cell} ipython3
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

:::{dropdown} What is a travel time matrix?
:open:
:color: light
:margin: 1 5 0 0

A travel time matrix is a tool and data set that allows researchers to study how
easily people can reach different destination within and beyond cities, and how
accessibility is influenced by factors such as the quality of public transport
systems, street networks, and land use patterns.

Typically, a travel time matrix is a table that shows the travel time (or other
travel costs) between all pairs of a set of locations in an urban area. The
locations represent typical origins and destinations, such as everyday services
and residential homes, or are a complete set of locations covering the entire
area wall-to-wall, such as census polygons or a regular grid.

Travel time matrices can then be used to analyse accessibility patterns,
evaluate the impacts of transport planning and land use policies, and to
identify in which areas and for which groups of people a city works best and
worst. This information can then help cities to become more equitable and more
sustainable, and foster a good quality of life for their residents.

Successful recent research that either used or produced travel time matrices
include the work of the Digital Geography Lab at the University of Helsinki
(e.g., {cite:t}`tenkanen_longitudinal_2020`, {cite:t}`salonen_modelling_2013`,
or {cite:t}`jarv_dynamic_2018`), the Mobility Network at the University of
Toronto (e.g., {cite:t}`farber_dynamic_pt_2017`,
{cite:t}`farber_temporal_variablity_2014`), and the Institute for Applied
Economic Research (IPEA, e.g., {cite:t}`braga_evaluating_2023`,
{cite:t}`herszenhut_impact_2022`).
:::


As briefly visited in [Quickstart](quickstart) and dicussed in detail in [Data
Requirements](data-requirements), fundamentally, two types of input data are
required for computing a travel time matrix:

- a transport network, and
- a set of origins and destinations

First, create a {class}`TransportNetwork<r5py.TransportNetwork>` and load an
OpenStreetMap extract of the Helsinki city centre as well as a public transport
schedule in GTFS format covering the same area:

```{code-cell} ipython3
:tags: [remove-output]

import r5py

transport_network = r5py.TransportNetwork(
    DATA_DIRECTORY / "São Paulo" / "spo_osm.pbf",
    [
        DATA_DIRECTORY / "São Paulo" / "spo_gtfs.zip",
    ]
)
```

Studies that compare accessibility (*potential* mobility) between different
neighbourhoods tend to use a regular grid of points that covers the study area
as origins or destinations. Recently, hexagonal grids, such as Uber’s [H3
indexing system](https://h3geo.org/) have gained popularity, as they assure
equidistant neighbourhood relationships (all neighbouring grid cells’ centroids
are at the same distance; in a grid of squares, the diagonal neighbours are
roughly 41% further than the horizontal and vertical ones).

```{code-cell} ipython3
import h3
import shapely

HELSINKI_CENTRE = shapely.box(24.9318, 60.1550, 24.9535, 60.1751)

SAO_PAULO_CENTRE = shapely.box(-46.650, -23.558, -46.620, -23.531)
```

```{code-cell} ipython3

```

```{code-cell} ipython3
h3.Polygon(list(SAO_PAULO_CENTRE.exterior.coords))
```

```{code-cell} ipython3
ZOOM_LEVEL = 9

h3_cells = [
    (cell, shapely.Polygon(h3.cell_to_boundary(cell)))
    for cell in h3.polygon_to_cells(h3.Polygon(list(SAO_PAULO_CENTRE.exterior.coords)), ZOOM_LEVEL)
]

import geopandas

hexagon_grid = geopandas.GeoDataFrame(
    {
        "id": [cell[0] for cell in h3_cells],
        "geometry": [cell[1] for cell in h3_cells]
    },
    crs="EPSG:4326"
)
hexagon_grid
```

```{code-cell} ipython3
import pandas
hexagon_grid = pandas.read_csv(DATA_DIRECTORY / "São Paulo" / "spo_hexgrid.csv")
hexagon_grid["geometry"] = hexagon_grid["id"].apply(lambda id : shapely.Polygon(h3.cell_to_boundary(id, True)))
hexagon_grid = geopandas.GeoDataFrame(hexagon_grid, crs="EPSG:4326")
hexagon_grid
```

```{code-cell} ipython3
hexagon_grid.explore()
```

```{code-cell} ipython3
origins = hexagon_grid.copy()
origins["geometry"] = origins.geometry.centroid
```

```{code-cell} ipython3
import datetime

travel_time_matrix = r5py.TravelTimeMatrixComputer(
    transport_network,
    origins=origins,
    transport_modes=[r5py.TransportMode.TRANSIT],
    departure=datetime.datetime(2019,5,13, 14, 0, 0),
).compute_travel_times()
travel_time_matrix
```

## Bibliography

:::{bibliography}
:filter: docname in docnames
:::
