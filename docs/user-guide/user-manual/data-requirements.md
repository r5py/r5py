# Data requirements

## Data for creating a routable network

When calculating travel times with *r5py*, you typically need three types of
datasets:

:::::{grid} 1 1 3 3

::::{grid-item-card}
a **road network** dataset from [OpenStreetMap
(OSM)](https://wiki.openstreetmap.org/wiki/Data) in [*Protocol Buffer Binary*
(`.pbf`)](https://wiki.openstreetmap.org/wiki/PBF_Format) format (mandatory):

These data are used for finding the fastest routes and calculating the travel
times for walking, cycling and driving. In addition, these data are used for
walking/cycling legs to, from, or between stops when routing with public
transport.
::::

::::{grid-item-card}
a **public transport schedule** dataset in [*General Transit Feed
Specification*](https://en.wikipedia.org/wiki/GTFS) format (optional):

These data contain all information necessary to calculate travel times on
public transport, such as the stops, routes, trips and schedules of busses,
trams, trains, and other vehicles.
::::

::::{grid-item-card}
a **digital elevation model** in
[*GeoTIFF*](https://en.wikipedia.org/wiki/GeoTIFF) format (optional):

These data can be used to model the terrain. They allow travel times to include the extra effort necessary to climb slopes on a bicycle or walking. This includes the walking trips to a public transport stop, or when changing from one line to another.
::::

::::{grid-item}
:columns: 12

(data-preprocessing)=

:::{admonition} Data pre-processing
:class: hint

Often, it is useful to *crop an [OSM extract](#where-to-obtain-such-datasets)*
beforehand, or to *add other cost factors* to the data (e.g., to account for
slope). Check the detailed instructions for data preparation on the [Conveyal
website](https://docs.conveyal.com/prepare-inputs#preparing-the-osm-data), and
use the tools in [this
repository](https://github.com/RSGInc/ladot_analysis_dataprep) to add
customised costs for pedestrian and cycling analyses.

*R5py* automatically *combines multiple GTFS data sets*. This is useful when you study
areas covered by more than one transit authority, or when data from different
modes of transport, such as bus and metro, are available in separate GTFS
feeds.
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
    cities. *Deprecated: will be replaced by Mobility Database*.


#### Digital elevation models in GeoTIFF format

  - *Your local municipality’s, county’s, or regional *Open Governmental Data
    (OGD)* portal*: many cities and regions across the world share detailed
    geographical data, including digital elevation models. They might also be
    called ‘height models’, or be hidden with complicated-to-use LIDAR point
    cloud data sets.
  - [OpenDEM](https://www.opendem.info) maintains a list of freely available
    high-resolution elevation data sets
  - [EU-DEM](http://www.eea.europa.eu/data-and-maps/data/eu-dem#tab-metadata),
    the ‘digital elevation model over Europe’ covers the 39 member countries of
    the European environment agency


(check-gtfs-files)=

:::{admonition} Check GTFS files
:class: tip

At times, it is worth to spot-check GTFS data sets downloaded from third-party
websites for validity, and to assert that they cover the time period and
geographic extent of a study area. 

*MobilityData*’s [GTFS
Validator](https://github.com/MobilityData/gtfs-validator) is a cross-platform
Java tool to check file integrity, data types, and compliance with the GTFS
standard. They also provide an [online
version](https://gtfs-validator.mobilitydata.org/) where you can upload a feed
to check against the reference and best practices.

[*GTFS-Lite*](https://gtfs-lite.readthedocs.io/) is a Python package to read
GTFS data sets into {class}`gtfslite.gtfs.GTFS` objects that store the
information on stops, routes, fares, etc., in {class}`pandas.DataFrame`s. Use
{meth}`GTFS.routes_summary()<gtfslite.gtfs.GTFS.routes_summary()>`,
{meth}`GTFS.stop_summary()<gtfslite.gtfs.GTFS.stop_summary()>`, and
{meth}`GTFS.summary()<gtfslite.gtfs.GTFS.summary()>` to gain a quick overview
of the scope of a GTFS data set.

:::


## Origin and destination locations

In addition to OSM and GTFS datasets, you need data that represent the origin
and destination locations (OD-data) of routes. *R5py* accepts data sets as
{class}`geopandas.GeoDataFrame`s.

Use {func}`geopandas.read_file()` to read data sets from files in one of the
many geospatial data formats, such as *GeoPackage*, *GeoJSON*, or *ESRI
Shapefile*.

If your data is in a non-spatial file format, such as spreadsheets, or CSV
files with columns representing the latitude and longitude coordinates, [follow
these
instructions](https://geopandas.org/en/stable/gallery/create_geopandas_from_pandas.html)
to convert them into a {class}`geopandas.GeoDataFrame`.


## Sample data sets

In this documentation, we use some sample data sets that you can [install
separately](../installation/installation.md#sample-data-sets). In particular,
the sample data comprises of the following data sets:

- Helsinki, Finland
  - A population grid data set of Helsinki city centre, obtained from the
    [Helsinki Region Environmental
    Services](https://www.hsy.fi/en/environmental-information/open-data/avoin-data---sivut/population-grid-of-helsinki-metropolitan-area/)
    (HSY), licensed under a Creative Commons By Attribution 4.0.
  
  - An OpenStreetMap extract covering Helsinki (© OpenStreetMap contributors,
    [ODbL license](https://www.openstreetmap.org/copyright))
  
  - A GTFS public transport schedule dataset for Helsinki, cropped and minimised
    from the official open-data download from *Helsingin seudun liikenne*’s
    (HSL) [open data web page](https://www.hsl.fi/en/hsl/open-data/) published
    under a Creative Commons By Attribution 4.0 license.

  - An elevation model for Helsinki, cropped to cover the extent of the other
    data sets, and downloaded from the [City of
    Helsinki](https://hri.fi/data/en_GB/dataset/helsingin-korkeusmalli),
    published under a Creative Commons By Attribution 4.0 license.
    
- São Paulo, Brazil
  - A population grid data set of São Paulo city centre, obtained from the
    [Access to Opportunities
    Project](https://www.ipea.gov.br/acessooportunidades/en/) conducted at the
    Institute for Applied Economic Research - Ipea, Brazil.
  
  - An OpenStreetMap extract covering São Paulo city centre (© OpenStreetMap
    contributors, [ODbL license](https://www.openstreetmap.org/copyright)).
  
  - A GTFS public transport schedule dataset for São Paulo, cropped and minimised
    from the official open-data download from *SPTRANS*’s
    [open data web page](https://www.sptrans.com.br/desenvolvedores/) (intended
    for open use, but no license specified).
