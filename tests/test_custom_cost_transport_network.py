#!/usr/bin/env python3


import pytest
import pytest_lazy_fixtures

import r5py


try:
    import com.conveyal.r5.rastercost.CustomCostField  # noqa: F401
    R5_SUPPORTS_CUSTOM_COSTS = True
except ImportError:
    R5_SUPPORTS_CUSTOM_COSTS = False

try:
    import com.conveyal.r5.rastercost.EdgeCustomCostPreCalculator  # noqa: F401
    R5_SUPPORTS_PRECALCULATE_COSTS = True
except ImportError:
    R5_SUPPORTS_PRECALCULATE_COSTS = False


@pytest.mark.skipif(
    not R5_SUPPORTS_CUSTOM_COSTS,
    reason="R5 jar does not support custom costs",
)
class Test_CustomCostTransportNetwork:
    """Test the CustomCostTransportNetwork and custom cost related logic."""

    @pytest.mark.parametrize(
        ("custom_costs",),
        (
            (pytest_lazy_fixtures.lf("custom_costs_1"),),
            (pytest_lazy_fixtures.lf("custom_costs_2"),),
            (pytest_lazy_fixtures.lf("custom_costs_multiple"),),
        )
    )
    def test_init(
        self,
        osm_pbf_file_path,
        gtfs_file_path,
        custom_costs,
    ):
        transport_network = r5py.CustomCostTransportNetwork(
            osm_pbf_file_path,
            [gtfs_file_path],
            custom_costs,
        )
        assert isinstance(transport_network, r5py.CustomCostTransportNetwork)
        assert isinstance(transport_network, r5py.TransportNetwork)
