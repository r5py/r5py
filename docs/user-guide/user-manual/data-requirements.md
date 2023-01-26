# Data requirements

## Data for creating a routable network

When calculating travel times with *r5py*, you typically need two types of
datasets:

:::::{grid} 1 1 2 2

::::{grid-item-card}
a **road network** dataset from [OpenStreetMap
(OSM)](https://wiki.openstreetmap.org/wiki/Data) in [*Protocol Buffer Binary*
(`.pbf`)](https://wiki.openstreetmap.org/wiki/PBF_Format) format:

These data are used for finding the fastest routes and calculating the travel
times for walking, cycling and driving. In addition, these data are used
for walking/cycling legs between stops when routing with public transport.
::::

::::{grid-item-card}
a **public transport schedule** dataset in [*General Transit Feed
Specification*](https://en.wikipedia.org/wiki/GTFS) format (optional):

These data contain all information necessary to calculate travel times on
public transport, such as the stops, routes, trips and schedules of busses,
trams, trains, and other vehicles.
::::

::::{grid-item}
:columns: 12

:::{admonition} Data pre-processing
:class: hint

Often, it is useful to *crop an [OSM extract](#where-to-obtain-such-datasets)*
beforehand, or to *add other cost factors* to the data (e.g., to account for
slope). Check the detailed instructions for data preparation on the [Conveyal
website](https://docs.conveyal.com/prepare-inputs#preparing-the-osm-data), and
use the tools in [this
repository](https://github.com/RSGInc/ladot_analysis_dataprep) to add
customised costs for pedestrian and cycling analyses.

*R5py* can *combine multiple GTFS data sets*. This is useful when you study
areas covered by more than one transit authority, or when data from different
modes of transport, such as bus and metro, are available in separate GTFS
feeds, only.
:::
::::

:::::

### Where to obtain such datasets?

Here are a few places from where you can download the datasets for creating the
routable network. This list is of course by no means comprehensive, and [you are
very welcome to add additional data sources](/contributing/CONTRIBUTING) that
you are aware of.

#### OpenStreetMap data in PBF format

- [pydriosm](https://pydriosm.readthedocs.io/en/latest/quick-start.html#download-data)
  is a Python package for downloading OSM extracts from GeoFabrik and BBBike.
- [pyrosm](https://pyrosm.readthedocs.io/en/latest/basics.html#protobuf-file-what-is-it-and-how-to-get-one)
  is a Python package for creating street networks from OSM extracts, and
  includes tools to download OSM extracts from GeoFabrik and BBBike
- [GeoFabrik](http://download.geofabrik.de/) is a website offering OSM extracts
  for free download, covering many pre-defined areas (continents, countries,
  regions, etc.)
- [BBBike](https://download.bbbike.org/osm/bbbike/) is a website that offers OSM
  extracts for free download, covering many pre-defined areas, including
  individual city’s extents, and also supports data [downloads cut to custom
  extents](https://extract.bbbike.org/)
- [Protomaps](https://protomaps.com/downloads/osm) is a website that allows you
  to download OSM extracts for a custom area of interest, drawn in an
  interactive map, or taken from an uploaded polygon feature.


#### Public transport schedules in GTFS format

  - *Your local transit authority, city works, or public transport company*:
    most of the time, you will find the most accurate and most up-to-date GTFS
    schedule files available locally, usually as an open-data download. If you
    cannot find a download, ask nicely, many transport authorities are happy to
    share
  - [Transitland](https://www.transit.land/operators) is an online data platform
    that collects GTFS data from 2500 public transport operators world-wide.
    Their database includes historical data sets.
  - [Mobility Database](https://database.mobilitydata.org) is an online repository
    storing current and historical GTFS data of 1800 operators from around the
    globe, run by a non-profit organisation. Already functional, but still being
    built, set to replace Transitfeeds (see below)
  - [Transitfeeds](https://transitfeeds.com/) is an easy to navigate website
    that hosts up-to-date and historical GTFS data for many countries and
    cities. *Deprecated: will be replaced by* Mobility Database.


## Origin and destination locations

In addition to OSM and GTFS datasets, you need data that represents the origin
and destination locations (OD-data) of routes. These data, if stored in one of
the many geospatial data formats, such as *GeoPackage*, *GeoJSON*, or *ESRI
Shapefile*, can be read by {meth}`geopandas<geopandas.read_file()>` that can be
used directly in *r5py*.


## Sample datasets

In this documentation, we use some open data sets, that you can also find in the
[source code
repository](https://github.com/r5py/r5py/tree/main/docs/_static/data/). In
particular, the sample data comprises of the following data sets:

- A population grid data set of Helsinki city centre, obtained from the
  [Helsinki Region Environmental
  Services](https://www.hsy.fi/en/environmental-information/open-data/avoin-data---sivut/population-grid-of-helsinki-metropolitan-area/)
  (HSY), licensed under a Creative Commons By Attribution 4.0.

- An OpenStreetMap extract covering Helsinki (© OpenStreetMap contributors,
  [ODbL license](https://www.openstreetmap.org/copyright))

- A GTFS public transport schedule dataset for Helsinki, cropped and minimised
  from the official open-data download from *Helsingin seudun liikenne*’s (HSL)
  [open data web page](https://github.com/r5py/r5py/tree/main/docs/_static/data/),
  licensed under a Creative Commons By Attribution 4.0.
