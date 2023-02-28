#!/usr/bin/env python3

import pytest
import shapely

import r5py


class Test_StreetLayer:
    @pytest.mark.parametrize(
        ["point", "snapped_point"],
        [
            (
                shapely.Point(24.934716339546334, 60.162003377483465),
                shapely.Point(24.9344161, 60.1620914),
            ),
            (
                shapely.Point(24.93472078921679, 60.159759479145855),
                shapely.Point(24.935045, 60.1598117),
            ),
            (
                shapely.Point(24.934725238091787, 60.157515624929495),
                shapely.Point(24.9345478, 60.1575712),
            ),
            (
                shapely.Point(24.934729686260493, 60.15527176994737),
                shapely.Point(24.9345898, 60.1552307),
            ),
            (
                shapely.Point(24.93919381647808, 60.17546866945838),
                shapely.Point(24.9392248, 60.1754825),
            ),
            (
                shapely.Point(24.93920625448821, 60.16873712001135),
                shapely.Point(24.9395336, 60.1688809),
            ),
            (
                shapely.Point(24.939210399174772, 60.16649326866454),
                shapely.Point(24.9392062, 60.166541),
            ),
            (
                shapely.Point(24.939214543203153, 60.16424941655202),
                shapely.Point(24.9395105, 60.1641026),
            ),
            (
                shapely.Point(24.939218686656393, 60.16200551878885),
                shapely.Point(24.9394813, 60.1620553),
            ),
            (
                shapely.Point(24.93922282945177, 60.15976162025793),
                shapely.Point(24.9391651, 60.1597873),
            ),
            (
                shapely.Point(24.93922697150651, 60.157517765848276),
                shapely.Point(24.9392257, 60.1574796),
            ),
            (
                shapely.Point(24.93923111290369, 60.15527391067289),
                shapely.Point(24.9393653, 60.1553187),
            ),
            (
                shapely.Point(24.94369793061261, 60.1754706588567),
                shapely.Point(24.9440337, 60.1754045),
            ),
            (
                shapely.Point(24.943701770118057, 60.17322680962688),
                shapely.Point(24.9437021, 60.1731434),
            ),
            (
                shapely.Point(24.943705609013687, 60.17098295963162),
                shapely.Point(24.9433897, 60.1708795),
            ),
            (
                shapely.Point(24.943709447299632, 60.16873910887079),
                shapely.Point(24.9437092, 60.1687734),
            ),
            (
                shapely.Point(24.94371328497602, 60.166495257344394),
                shapely.Point(24.9437549, 60.1664853),
            ),
            (
                shapely.Point(24.943717122043, 60.16425140505232),
                shapely.Point(24.9438497, 60.1643061),
            ),
            (
                shapely.Point(24.943720958577437, 60.162007507109614),
                shapely.Point(24.9437158, 60.1620892),
            ),
            (
                shapely.Point(24.94372479450272, 60.159763608399196),
                shapely.Point(24.9440714, 60.1598923),
            ),
            (
                shapely.Point(24.943728629742253, 60.15751975381008),
                shapely.Point(24.9439189, 60.1575247),
            ),
            (
                shapely.Point(24.94373246437293, 60.15527589845523),
                shapely.Point(24.9437321, 60.1552857),
            ),
            (
                shapely.Point(24.948205577705817, 60.17322864583047),
                shapely.Point(24.9482066, 60.1730688),
            ),
            (
                shapely.Point(24.94820910949361, 60.17098479566939),
                shapely.Point(24.9482103, 60.1707875),
            ),
            (
                shapely.Point(24.948216171386584, 60.166497093050616),
                shapely.Point(24.9478373, 60.1665188),
            ),
        ],
    )
    def test_find_split(self, transport_network, point, snapped_point):
        street_layer = transport_network.street_layer
        assert isinstance(street_layer, r5py.r5.StreetLayer)
        assert street_layer.find_split(point) == snapped_point
