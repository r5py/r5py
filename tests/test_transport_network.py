#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py
import com.conveyal.r5
import java.time


class Test_TransportNetwork:
    def test_init_from_files_and_dir_cover_same_extent(
        self, transport_network_from_test_files, transport_network_from_test_directory
    ):
        assert (
            transport_network_from_test_files._transport_network.getEnvelope()
            == transport_network_from_test_directory._transport_network.getEnvelope()
        )

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest.lazy_fixture("transport_network_from_test_files"),),
            (pytest.lazy_fixture("transport_network_from_test_directory"),),
        ],
    )
    def test_transport_network_java_object(self, transport_network):
        assert isinstance(
            transport_network._transport_network,
            com.conveyal.r5.transit.TransportNetwork,
        )

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest.lazy_fixture("transport_network_from_test_files"),),
            (pytest.lazy_fixture("transport_network_from_test_directory"),),
        ],
    )
    def test_context(self, transport_network):
        with transport_network as tn:
            assert isinstance(tn, r5py.TransportNetwork)
            assert tn == transport_network

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest.lazy_fixture("transport_network_from_test_files"),),
            (pytest.lazy_fixture("transport_network_from_test_directory"),),
        ],
    )
    def test_linkage_cache_java_object(self, transport_network):
        assert isinstance(
            transport_network.linkage_cache, com.conveyal.r5.analyst.LinkageCache
        )

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest.lazy_fixture("transport_network_from_test_files"),),
            (pytest.lazy_fixture("transport_network_from_test_directory"),),
        ],
    )
    def test_street_layer_java_object(self, transport_network):
        assert isinstance(
            transport_network.street_layer, com.conveyal.r5.streets.StreetLayer
        )

    @pytest.mark.parametrize(
        ["transport_network"],
        [
            (pytest.lazy_fixture("transport_network_from_test_files"),),
            (pytest.lazy_fixture("transport_network_from_test_directory"),),
        ],
    )
    def test_timezone(self, transport_network, gtfs_timezone_helsinki):
        assert isinstance(transport_network.timezone, java.time.ZoneId)
        assert transport_network.timezone.toString() == gtfs_timezone_helsinki
