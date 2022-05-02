#!/usr/bin/env python3


"""Test r5py."""


import datetime
import geopandas
import r5py


def main():
    """
    Test r5py.

    Loads some files I have laying around in my home folder,
    then computes a travel time matrix out of them.
    """
    osm_pbf = "../docs/data/kantakaupunki.osm.pbf"
    gtfs = ["../docs/data/GTFS.zip"]

    ykr_centroids = geopandas.read_file(
        "/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki/YKR_250m_PKS.gpkg",
        layer="YKR 250m Pääkaupunkiseutu centroids (EPSG:4326)",
    )

    # for debugging, only every 50th row
    ykr_centroids = ykr_centroids.iloc[::50, :]

    origins_destinations = ykr_centroids[["id", "geometry"]]

    travel_time_matrix = r5py.TravelTimeMatrix(
        (osm_pbf, gtfs, {}),
        origins_destinations,
        departure=datetime.datetime(year=2022, month=2, day=22, hour=8, minute=30),
        transport_modes=[r5py.TransitMode.TRANSIT],
        breakdown=True,
        percentiles=[25, 50, 75],
        # percentiles=[33],
        max_time=datetime.timedelta(hours=24)
    )

    request = travel_time_matrix.request
    print(request.max_time, request.max_time_walking, request.max_time_cycling)
    print(request.transport_modes, request.access_modes, request.egress_modes)

    travel_time_matrix.verbose = True

    results = travel_time_matrix.compute_travel_times()
    results.to_pickle("/tmp/ttm.zstd")

    return results


# linting trigger foobar bar


if __name__ == "__main__":
    main()
