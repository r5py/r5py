---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.8
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Usage

```python nbsphinx="hidden" tags=["remove-cell"]
# this cell is hidden from output
# it’s used to 
# - set sys.path to point to the local repo
# - make ipython show all outputs of each cell

# - set sys.path to point to the local repo
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path().absolute().parent.parent / "src"))

# - make ipython show all outputs of each cell
get_ipython().ast_node_interactivity = "all"
```

## Python

R5py exposes some of R5’s functionality via its [Python API](reference.html), in a syntax similar to r5r’s. At the time of this writing, only the computation of travel time matrices has been fully implemented. 

Below, you find a minimal example of computing a travel time matrix:

<!-- #region tags=[] -->
### Load transport network

Virtually all operations of r5py require a transport network. As input files to construct a transport network topology, r5py needs the following data sets:

- The street network in the form of an OpenStreetMap extract covering the study area, prepared according to the instructions at https://docs.conveyal.com/prepare-inputs#preparing-the-osm-data, and possibly annotated with LADOT tags (see https://github.com/RSGInc/ladot_analysis_dataprep).
- Public transport schedules in GTFS format (optional, r5py can combine multiple GTFS files)

In this example, we use data from Helsinki metropolitan area, which you can find in the source code repository of r5py in `docs/data/`. The street network is a cropped and filtered extract of OpenStreetMap (© OpenStreetMap contributors, [ODbL license](https://www.openstreetmap.org/copyright)), the GTFS transport schedule is a cropped and minimised copy of Helsingin seudun liikenne’s (HSL) open data set [Creative Commons BY 4.0](https://www.hsl.fi/hsl/avoin-data#aineistojen-kayttoehdot).

To import the street and public transport networks, instantiate an `r5py.TransportNetwork` with the file paths to the OSM extract and the GTFS files:
<!-- #endregion -->

```python
from r5py import TransportNetwork

transport_network = TransportNetwork(
    "../data/Helsinki/kantakaupunki.osm.pbf",
    [
        "../data/Helsinki/GTFS.zip"
    ]
)
```

### Compute a travel time matrix

A travel time matrix is a data set detailing the travel costs (e.g., time) from each point to each point in a set of origins and destinations in a study area. 

For the sake of this exercise, we have prepared a grid of points covering parts of Helsinki. The point dataset has been obtained from [Helsinki Region Environmental Services](https://www.hsy.fi/en/environmental-information/open-data/avoin-data---sivut/population-grid-of-helsinki-metropolitan-area/) (HSY) licensed under a Creative Commons By Attribution 4.0. The point data also contains information about residents of each 250 meter cell.

```python
import geopandas

grid_points = geopandas.read_file("../data/Helsinki/population_points_2020.gpkg")

grid_points.head()
```


We can now visualise the number of people living in each cell (the cells are represented by their centre point):


```python
grid_points.explore("population", cmap="Reds", marker_kwds={"radius": 12})
```

Now, to compute a travel time matrix between all `grid_points`, we first instantiate an `r5py.TravelTimeMatrixComputer` with the transport network we created earlier, and a list of origins (since we don’t specify a separate set of destinations, r5py will use the same points as destinations and produce a full set of origins and destinations). The constructor also accepts all parameters of [RegionalTask](reference.html#r5py.RegionalTask), such as transport modes, or walking speed. 

Calling `compute_travel_times()` on the instance will return a `pandas.DataFrame` with travel times between all points.

```python
import datetime

from r5py import TravelTimeMatrixComputer, TransitMode, LegMode


travel_time_matrix_computer = TravelTimeMatrixComputer(
    transport_network,
    origins=grid_points,
    departure=datetime.datetime(2022,2,22,8,30),
    transport_modes=[TransitMode.TRANSIT, LegMode.WALK],
    #percentiles=[1,25,50,75,99],
    #breakdown=True
)
travel_time_matrix = travel_time_matrix_computer.compute_travel_times()
travel_time_matrix
```

The values in the `travel_time` column are travel times between the points identified by `from_id` and `to_id`, in minutes. 

The median travel time to or from a certain point gives a good estimate of the overall accessibility to or from it, in relation to other points:

```python tags=[]
travel_time_matrix.groupby("from_id")["travel_time"].median()
```

```python
travel_time_matrix.groupby("from_id")["travel_time"].median().median()
```
