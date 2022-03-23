import pandas
import geopandas
import numpy
import r5p
import com.conveyal.r5

MAX_INT32 = (2 ** 31) - 1

transport_network = r5p.TransportNetwork(
    osm_pbf="/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki/paakaupunkiseutu.pbf",
    gtfs=[
        "/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki/GTFS.zip"
    ],
)

ykr_centroids = geopandas.read_file(
    "/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki/YKR_250m_PKS.gpkg",
    layer="YKR 250m Pääkaupunkiseutu centroids (EPSG:4326)",
)

origins = ykr_centroids[["id", "geometry"]]
destinations = ykr_centroids[["id", "geometry"]]

od_matrix = (
    origins.rename(columns={"id": "from_id", "geometry": "from_geometry"})
    .join(
        destinations.rename(columns={"id": "to_id", "geometry": "to_geometry"}),
        how="cross"
    )
)
od_matrix["travel_time"] = numpy.nan

# the following should be doable with a more elegant solution (groupby().apply(), or similar)
# but for now let’s keep the premature optimisation aside
count = 0
for from_id in origins.id:
    count += 1
    print(count, end="\r", flush=True)
    request = r5p.RegionalTask(
        transport_network,
        origin=origins.at[origins.id == from_id].geometry,
        destinations=destinations,
        transport_modes=[r5p.TransitMode.TRANSIT],
    )
    travel_time_computer = com.conveyal.r5.analyst.TravelTimeComputer(
        request, transport_network
    )
    results = travel_time_computer.computeTravelTimes()
    # od_matrix[od_matrix.from_id == from_id, "travel_time"] = results.travelTimes.getValues()[0]
    # od_matrix[od_matrix.from_id == from_id, "travel_time"] = results.travelTimes.getValues()[0]
    od_matrix[od_matrix.from_id == from_id] = (
        od_matrix[od_matrix.from_id == from_id].assign(
            travel_time=results.travelTimes.getValues()[0]
        )
    )

od_matrix[od_matrix.travel_time == MAX_INT32, "travel_time"] = numpy.nan

od_matrix.to_file("od_matrix.gpkg")
