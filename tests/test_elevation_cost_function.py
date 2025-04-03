#!/usr/bin/env python3


import pytest

import r5py


class TestElevationCostFunction:
    def test_some_weird_combinations(self):
        # not as a parametrized test as pytest has troubles with
        # functions as parametrized fixtures (tries to evaluate?)
        assert r5py.ElevationCostFunction("tobler") == r5py.ElevationCostFunction.TOBLER
        assert r5py.ElevationCostFunction("Tobler") == r5py.ElevationCostFunction.TOBLER
        assert r5py.ElevationCostFunction("tObLeR") == r5py.ElevationCostFunction.TOBLER
        assert r5py.ElevationCostFunction("TOBLER") == r5py.ElevationCostFunction.TOBLER
        assert (
            r5py.ElevationCostFunction("minetti") == r5py.ElevationCostFunction.MINETTI
        )
        assert (
            r5py.ElevationCostFunction("Minetti") == r5py.ElevationCostFunction.MINETTI
        )
        assert (
            r5py.ElevationCostFunction("mInEtTi") == r5py.ElevationCostFunction.MINETTI
        )
        assert (
            r5py.ElevationCostFunction("MINETTI") == r5py.ElevationCostFunction.MINETTI
        )

        with pytest.raises(ValueError):
            _ = r5py.ElevationCostFunction("FooBarInvalidCostFunction")
