#!/usr/bin/env python3


"""Test r5p."""


import datetime
import geopandas
import r5p


def main():
    """
    Test r5p.

    Loads some files I have laying around in my home folder,
    then computes a travel time matrix out of them.
    """
    osm_pbf = "/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki/paakaupunkiseutu.pbf"
    gtfs = ["/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki/GTFS.zip"]

    ykr_centroids = geopandas.read_file(
        "/home/christoph/Dokumente/Helsingin Yliopisto/Papers/Current/2021-10 Slawek’s paper/r5/Helsinki/YKR_250m_PKS.gpkg",
        layer="YKR 250m Pääkaupunkiseutu centroids (EPSG:4326)",
    )

    # # for debugging, only every 25th row
    # ykr_centroids = ykr_centroids.iloc[::25, :]

    origins_destinations = ykr_centroids[["id", "geometry"]]

    travel_time_matrix = r5p.TravelTimeMatrix(
        (osm_pbf, gtfs, {}),
        origins_destinations,
        departure=datetime.datetime(year=2022, month=2, day=22, hour=8, minute=30),
        transport_modes=[r5p.TransitMode.TRANSIT]
    )

    travel_time_matrix.verbose = True

    results = travel_time_matrix.compute_travel_times()
    results.to_csv("/tmp/ttm.csv")


if __name__ == "__main__":
    main()
