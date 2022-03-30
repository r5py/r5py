import geopandas
import numpy
import multiprocessing
import pandas
import shapely
import r5p
import com.conveyal.r5

MAX_INT32 = (2 ** 31) - 1
NUM_WORKERS = 2  # multiprocessing.cpu_count() + 1


def merge_points_into_linestring(dataframe):
    dataframe["geometry"] = dataframe[["from_geometry", "to_geometry"]].apply(shapely.geometry.LineString, axis=1)
    return dataframe


def set_max_travel_time_to_nan(dataframe):
    dataframe[dataframe.travel_time == MAX_INT32] = (
        dataframe[dataframe.travel_time == MAX_INT32].assign(travel_time=numpy.nan)
    )
    return dataframe


def main():
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

    # for debugging
    ykr_centroids = ykr_centroids.iloc[::25, :]

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
            origin=origins[origins.id == from_id].geometry,
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
    print(flush=True)
    transport_network = None
    request = None

    print("set_max_travel_time_to_nan")
    workers = multiprocessing.get_context("spawn").Pool(NUM_WORKERS)
    # workers = multiprocessing.Pool(NUM_WORKERS)
    od_matrix = pandas.concat(
        workers.map(
            set_max_travel_time_to_nan,
            numpy.array_split(od_matrix, NUM_WORKERS),
            100
        )
    )
    print("merge_points_into_linestring")
    od_matrix = pandas.concat(
        workers.map(
            merge_points_into_linestring,
            numpy.array_split(od_matrix, NUM_WORKERS),
            100
        )
    )

    # od_matrix[od_matrix.travel_time == MAX_INT32] = (
    #     od_matrix[od_matrix.travel_time == MAX_INT32].assign(travel_time=numpy.nan)
    # )
    # od_matrix["geometry"] = od_matrix[["from_geometry", "to_geometry"]].apply(lambda x: shapely.geometry.LineString([(x.from_geometry.x, x.from_geometry.y), (x.to_geometry.x, x.to_geometry.y)]), axis=1)

    print("drop columns")
    od_matrix = geopandas.GeoDataFrame(od_matrix[["from_id", "to_id", "travel_time", "geometry"]])
    print("save")
    od_matrix.to_file("od_matrix.gpkg")


if __name__ == "__main__":
    main()
