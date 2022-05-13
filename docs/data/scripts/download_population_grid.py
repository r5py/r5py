#!/usr/bin/env python3

"""Download a population grid data set from HSY’s WFS service."""

import geopandas


def main():
    """Download a population grid data set from HSY’s WFS service."""
    df = geopandas.read_file(
        "https://kartta.hsy.fi/geoserver/wfs"
        "?service=wfs"
        "&version=2.0.0"
        "&request=GetFeature"
        "&typeName=asuminen_ja_maankaytto:Vaestotietoruudukko_2020"
        "&srsName=EPSG:3857"
        "&bbox=2772500,8434300,2778415,8439059,EPSG:3857"
    ).set_crs("EPSG:3857")

    df = df[["asukkaita", "geometry"]].reset_index()
    df = df.rename(columns={"index": "id", "asukkaita": "population"})
    df.geometry = df.geometry.centroid
    df.to_crs("EPSG:4326").to_file("../population_points_2020.gpkg")

if __name__ == "__main__":
    main()