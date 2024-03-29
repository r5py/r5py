#!/usr/bin/env python3


import pyproj
import pytest
import shapely

import r5py


class TestGoodEnoughEquidistantCrs:
    @pytest.mark.parametrize(
        ["extent", "expected"],
        [
            (
                shapely.box(-180, -90, 180, 90),
                pyproj.CRS.from_epsg(3857),
            ),
            (
                shapely.Point((8, 9)),
                pyproj.CRS.from_epsg(32632),
            ),
            (
                shapely.LineString(
                    (
                        (24.9501156641155788, 60.16947122421193228),
                        (24.95352425020545439, 60.17556887351519634),
                        (24.96257830700666247, 60.2044859777149739),
                        (25.01556632713091588, 60.2265357685618099),
                        (24.90620106775895692, 60.19040368495365811),
                    )
                ),
                pyproj.CRS.from_epsg(32635),
            ),
            (
                shapely.Polygon(
                    (
                        (-46.63688, -23.53505),
                        (-46.62654, -23.53754),
                        (-46.62731, -23.53931),
                        (-46.62627, -23.54493),
                        (-46.62646, -23.54691),
                        (-46.62499, -23.55171),
                        (-46.62781, -23.55615),
                        (-46.63637, -23.55647),
                        (-46.64494, -23.55441),
                        (-46.64788, -23.54677),
                        (-46.64772, -23.54137),
                        (-46.64660, -23.54109),
                        (-46.64614, -23.53907),
                        (-46.64017, -23.53491),
                        (-46.63688, -23.53505),
                    )
                ),
                pyproj.CRS.from_epsg(32723),
            ),
        ],
    )
    def test_equidistant_crs(self, extent, expected):
        assert r5py.util.GoodEnoughEquidistantCrs(extent) == expected

    @pytest.mark.parametrize(
        [
            "extent",
        ],
        [
            (shapely.box(-180000, -90000, 180000, 90000),),
            (shapely.Point(800000, 9000000),),
            (
                shapely.LineString(
                    (
                        (249501156641155788, 6016947122421193228),
                        (2495352425020545439, 6017556887351519634),
                        (2496257830700666247, 602044859777149739),
                        (2501556632713091588, 602265357685618099),
                        (2490620106775895692, 6019040368495365811),
                    )
                ),
            ),
            (
                shapely.Polygon(
                    (
                        (-4663688, -2353505),
                        (-4662654, -2353754),
                        (-4662731, -2353931),
                        (-4662627, -2354493),
                        (-4662646, -2354691),
                        (-4662499, -2355171),
                        (-4662781, -2355615),
                        (-4663637, -2355647),
                        (-4664494, -2355441),
                        (-4664788, -2354677),
                        (-4664772, -2354137),
                        (-4664660, -2354109),
                        (-4664614, -2353907),
                        (-4664017, -2353491),
                        (-4663688, -2353505),
                    )
                ),
            ),
        ],
    )
    def test_invalid_equidistant_crs(self, extent):
        with pytest.raises(r5py.util.exceptions.UnexpectedCrsError):
            _ = r5py.util.GoodEnoughEquidistantCrs(extent)
