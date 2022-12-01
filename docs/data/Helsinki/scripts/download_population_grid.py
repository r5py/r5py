#!/usr/bin/env python3

"""Download a population grid data set from HSY’s WFS service."""

import geopandas
import pathlib


def main():
    """Download a population grid data set from HSY’s WFS service."""
    # Where to save the downloaded data sets? One directory up from this script
    OUTPUT_DIRECTORY = pathlib.Path().absolute().parent

    # Download vector data set for the specified bounding box
    # in the upstream native reference system ETRS GK-25 (EPSG:3879),
    # then reproject it to WGS-84 (EPSG:4326)
    df = (
        geopandas.read_file(
            "https://kartta.hsy.fi/geoserver/wfs"
            "?service=wfs"
            "&version=2.0.0"
            "&request=GetFeature"
            "&typeName=asuminen_ja_maankaytto:Vaestotietoruudukko_2020"
            "&srsName=EPSG:3879"
            "&bbox=25494767,6671328,25497720,6673701,EPSG:3879"
        )
        .set_crs("EPSG:3879")
        .to_crs("EPSG:4326")
    )

    # discard most columns (detailed data), and add a sequential index column
    df = df[["asukkaita", "geometry"]].reset_index()

    # rename columns from Finnish to English, also `index` to `id`
    df = df.rename(columns={"index": "id", "asukkaita": "population"})

    # save the resulting data to a file
    df.to_file(OUTPUT_DIRECTORY / "population_grid_2020.gpkg")

    # derive a data set containing centroid points instead of grid cell polygons
    df.geometry = df.geometry.centroid
    # and save the resulting data to another file
    df.to_file(OUTPUT_DIRECTORY / "population_points_2020.gpkg")


if __name__ == "__main__":
    main()
