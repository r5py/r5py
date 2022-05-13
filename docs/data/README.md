# Data

Details about the bundled datasets.

### GTFS.zip

General Transit Feed Specification ([GTFS](https://developers.google.com/transit/gtfs/reference)) data representing 
the public transport schedules, stop locations, lines, etc. 
The data was created by Helsinki Region Transport (HLS) and obtained from [TransitFeeds.com](https://transitfeeds.com/p/helsinki-regional-transport/735).
GTFS data is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

To reduce the size of the sample dataset, it was cropped to cover parts of the City of Helsinki.

### kantakaupunki.osm.pbf

A sample dataset representing OpenStreetMap data in protocolbuffer binary format (PBF), 
which was obtained from [Geofabrik](https://download.geofabrik.de/europe/finland.html). 
The data is licensed under [OpenStreetMap license](https://www.openstreetmap.org/copyright).

We used [osmium](https://osmcode.org/osmium-tool/) to crop the data to the given extent.

### population_points_2020.gpkg

A sample dataset distributed with the package representing populated points in Helsinki. 
The data is obtained from Helsinki Region Environmental Services (HSY). 
The data is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 

The data is downloaded using HSY WFS service (see [the script](scripts/download_population_grid.py)) and modified slightly 
to make it straightforward to use in r5py documentation, namely we:

- reindex the data
- rename the columns from Finnish to English
- extract centroids from the grid polygons, and
- reproject the data from "EPSG:3857" to "EPSG:4326"