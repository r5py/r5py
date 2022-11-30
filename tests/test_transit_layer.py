#!/usr/bin/env python3


import pytest

from r5py.r5.transit_layer import TransitLayer


class TestTransitLayer:
    def test_uninitialised_transit_layer_start_date(self):
        transit_layer = TransitLayer()
        with pytest.raises((AttributeError, ValueError)):
            assert transit_layer.start_date < transit_layer.end_date

    def test_uninitialised_transit_layer_end_date(self):
        transit_layer = TransitLayer()
        with pytest.raises((AttributeError, ValueError)):
            assert transit_layer.end_date > transit_layer.start_date
