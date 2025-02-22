#!/usr/bin/env python3


"""Fixtures related to regional tasks and routing parameters."""


import datetime

import pytest


@pytest.fixture(scope="session")
def departure_datetime():
    """Return the departure time to run tests for."""
    yield datetime.datetime(2022, 2, 22, 8, 30)


@pytest.fixture
def regional_task(
    population_grid_points,
    transport_network,
    departure_datetime,
):
    """Return an initialised `r5py.RegionalTask`."""
    import r5py

    regional_task = r5py.RegionalTask(
        transport_network,
        population_grid_points.at[1, "geometry"],
        population_grid_points,
        departure=departure_datetime,
    )
    yield regional_task
