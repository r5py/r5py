# Data

Details about the bundled datasets.

### GTFS.zip

General Transit Feed Specification ([GTFS](https://developers.google.com/transit/gtfs/reference)) data representing 
the public transport schedules, stop locations, lines, etc. 
The data was created by Helsinki Region Transport (HLS) and obtained from [TransitFeeds.com](https://transitfeeds.com/p/helsinki-regional-transport/735).
GTFS data is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

To reduce the size of the sample dataset, it was cropped to cover only parts of the City of Helsinki, and a limited time frame only.

### kantakaupunki.osm.pbf

A sample dataset representing OpenStreetMap data in protocolbuffer binary format (PBF), 
which was obtained from [Geofabrik](https://download.geofabrik.de/europe/finland.html). 
The data is licensed under the [Open Data Commons Open Database License (ODbL)](https://www.openstreetmap.org/copyright).

We used [osmium](https://osmcode.org/osmium-tool/) to crop the data to the given extent.

### population_points_2020.gpkg, population_grid_2020.gpkg

A sample dataset distributed with the package representing populated points in Helsinki. 
The data is obtained from Helsinki Region Environmental Services (HSY). 
The data is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 

The data is downloaded from the Helsinki Region Environmental Services’ (HSY) *Web Feature Service (WFS)* endpoint (see the [Helsinki Region Infoshare’s data description](https://hri.fi/data/en_GB/dataset/vaestotietoruudukko)). We used [a script](scripts/download_population_grid.py), that we share with this package, to download the data set and adapt it to the requirements of r5py’s documentation. Namely, we:

- reindexed the data,
- omitted some columns,
- renamed the remaining columns from Finnish to English
- reprojected the data to "EPSG:4326", and
- extracted centroids from the grid polygons (for the point data set)
