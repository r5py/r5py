#!/usr/bin/env python3


"""Determine if an upstream R5 jar is used."""


import pytest


@pytest.fixture(scope="session")
def can_compute_detailed_route_geometries():
    """Determine if this R5 jar can output detailed route geometries"."""
    from r5py.util import start_jvm

    start_jvm()

    import com.conveyal.r5

    yield bool(com.conveyal.r5.transit.TransitLayer.SAVE_SHAPES)
