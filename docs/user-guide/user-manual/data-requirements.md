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
for walking/cycling legs between stops when routing with transit.
::::

::::{grid-item-card}
a **transit schedule** dataset in [*General Transit Feed
Specification*](https://en.wikipedia.org/wiki/GTFS) format (optional):

These data contain all information necessary to calculate travel times on
public transport, such as the stops, routes, trips and schedules of busses,
trams, trains, and other vehicles.
::::

::::{grid-item}
:columns: 12

:::{admonition} Data pre-processing
:class: hint

Often, it is useful to *crop an [OSM extract](#where-to-get-these-datasets)*
beforehand, or to *add other cost factors* to the data (e.g., to account for
slope). Check the detailed instructions for data preparation on the [Conveyal
website](https://docs.conveyal.com/prepare-inputs#preparing-the-osm-data), and
use the tools in [this
repository](https://github.com/RSGInc/ladot_analysis_dataprep) to add
customised costs for pedestrian and cycling analyses.

*r5py* can *combine multiple GTFS data sets*. This is useful when you study
areas covered by more than one transport authority, or when data from different
modes of transport, such as bus and metro, are available in separate GTFS
feeds, only.
:::
::::

:::::



## Origin and destination locations

In addition to OSM and GTFS datasets, you need data that represents the origin
and destination locations (OD-data) for routings. This data is typically stored
in one of the geospatial data formats, such as Shapefile, GeoJSON or
GeoPackage. As *r5py* is built on top of `geopandas`, it is easy to read
OD-data from various different data formats.


## Where to get these datasets?

Here are a few places from where you can download the datasets for creating the routable network:

- **OpenStreetMap data in PBF-format**:

  - [pyrosm](https://pyrosm.readthedocs.io/en/latest/basics.html#protobuf-file-what-is-it-and-how-to-get-one)  library. Allows downloading data directly from Python (based on GeoFabrik and BBBike).
  - [pydriosm](https://pydriosm.readthedocs.io/en/latest/quick-start.html#download-data) library. Allows downloading data directly from Python (based on GeoFabrik and BBBike).
  - [GeoFabrik](http://download.geofabrik.de/) website. Has data extracts for many pre-defined areas (countries, regions, etc).
  - [BBBike](https://download.bbbike.org/osm/bbbike/) website. Has data extracts readily available for many cities across the world. Also supports downloading data by [specifying your own area or interest](https://extract.bbbike.org/).
  - [Protomaps](https://protomaps.com/downloads/osm) website. Allows to download the data with custom extent by specifying your own area of interest.


- **GTFS data**:
  - [Transitfeeds](https://transitfeeds.com/) website. Easy to navigate and find GTFS data for different countries and cities. Includes current and historical GTFS data. Notice: The site will be deprecated in the future.
  - [Mobility Database](https://database.mobilitydata.org) website. Will eventually replace TransitFeeds.
  - [Transitland](https://www.transit.land/operators) website. Find data based on country, operator or feed name. Includes current and historical GTFS data.

## Sample datasets

In the following tutorial, we use various open source datasets:
- The point dataset for Helsinki has been obtained from [Helsinki Region Environmental Services](https://www.hsy.fi/en/environmental-information/open-data/avoin-data---sivut/population-grid-of-helsinki-metropolitan-area/) (HSY) licensed under a Creative Commons By Attribution 4.0.
- The street network for Helsinki is a cropped and filtered extract of OpenStreetMap (© OpenStreetMap contributors, [ODbL license](https://www.openstreetmap.org/copyright))
- The GTFS transport schedule dataset for Helsinki is a cropped and minimised copy of Helsingin seudun liikenne’s (HSL) open dataset ([Creative Commons BY 4.0](https://www.hsl.fi/hsl/avoin-data#aineistojen-kayttoehdot)).
