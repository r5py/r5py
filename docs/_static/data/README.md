# Data

Details about the bundled datasets.


## Helsinki

### `GTFS.zip`

General Transit Feed Specification ([GTFS](https://developers.google.com/transit/gtfs/reference))
data representing the public transport schedules, stop locations, lines, etc.
The data was created by Helsinki Region Transport (HLS) and obtained from
[TransitFeeds.com](https://transitfeeds.com/p/helsinki-regional-transport/735).

This GTFS data set is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).


### `kantakaupunki.osm.pbf`

A sample dataset representing OpenStreetMap data in protocolbuffer binary format (PBF),
which was obtained from [Geofabrik](https://download.geofabrik.de/europe/finland.html).
The data is licensed under the [Open Data Commons Open Database License (ODbL)](https://www.openstreetmap.org/copyright).

We used [osmium](https://osmcode.org/osmium-tool/) to crop the data to the given extent.


### `population_points_2020.gpkg`, `population_grid_2020.gpkg`

A sample dataset representing the population of Helsinki.
The data is obtained from Helsinki Region Environmental Services (HSY).
The data is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The data is downloaded from the Helsinki Region Environmental Services’ (HSY)
*Web Feature Service (WFS)* endpoint (see the
[Helsinki Region Infoshare’s data description](https://hri.fi/data/en_GB/dataset/vaestotietoruudukko)).
We used [a script](scripts/download_population_grid.py), that we share with this package, to download
the data set and adapt it to the requirements of r5py’s documentation. Namely, we:

- reindexed the data,
- omitted some columns,
- renamed the remaining columns from Finnish to English
- reprojected the data to "EPSG:4326", and
- extracted centroids from the grid polygons (for the point data set)


## São Paulo

### `spo_gtfs.zip`

General Transit Feed Specification ([GTFS](https://developers.google.com/transit/gtfs/reference))
data representing the public transport schedules, stop locations, lines, etc.

In contrast to the GTFS data set for Helsinki, the São Paulo data also has schedules expressed
in frequencies rather than fixed departure times.

[This data set has been published by São Paulo Transporte S/A, the public transport company of the
city of São Paulo for open use, but without a specific license specified.](https://www.sptrans.com.br/desenvolvedores)


### `spo_osm.pbf`

A sample dataset representing OpenStreetMap data in protocolbuffer binary format (PBF),
which was obtained from [Geofabrik](https://download.geofabrik.de/europe/finland.html).
The data is licensed under the [Open Data Commons Open Database License (ODbL)](https://www.openstreetmap.org/copyright).


### `spo_hexgrid.csv`

A regular, hexagonally distributed, point grid data set over the extent of São Paulo, created by
the authors of [r5r](https://github.com/ipeaGIT/r5r/tree/master/r-package/inst/extdata/spo). This data
set is used in some of the tests.
