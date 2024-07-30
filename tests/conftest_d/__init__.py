#!/usr/bin/env python3


"""Fixtures to be used in r5py tests."""


from .custom_costs import (
    custom_costs_1,
    custom_costs_2,
    custom_costs_multiple,
    custom_costs_transport_network,
)

from .destinations import (
    population_grid,
    population_grid_points,
    population_grid_points_first_three,
    population_grid_points_second_three,
    population_grid_points_four,
    snapped_population_grid_points,
    unreachable_stops,
    unsnappable_points,
)

from .origins import (
    origin_point,
    origins_invalid_duplicate_ids,
    origins_invalid_no_id,
    origins_valid_ids,
)

from .r5_jar import (
    r5_jar_cached,
    r5_jar_cached_invalid,
    r5_jar_sha256,
    r5_jar_sha256_github_error_message_when_posting,
    r5_jar_sha256_invalid,
    r5_jar_url,
)

from .routing_parameters import (
    departure_datetime,
    regional_task,
)

from .routing_results import (
    detailed_itineraries_bicycle,
    detailed_itineraries_car,
    detailed_itineraries_transit,
    detailed_itineraries_walk,
    walking_details_not_snapped,
    walking_details_snapped,
    walking_times_not_snapped,
    walking_times_snapped,
)

from .sample_data import (
    sample_data_set_sha256,
    sample_data_set_url,
)

from .transport_network import (
    gtfs_file_path,
    gtfs_timezone_helsinki,
    not_a_gtfs_file,
    osm_pbf_file_path,
    transport_network,
    transport_network_files_tuple,
    transport_network_from_test_directory,
    transport_network_from_test_files,
    transport_network_from_test_files_without_gtfs,
)

__all__ = [
    "custom_costs_1",
    "custom_costs_2",
    "custom_costs_multiple",
    "custom_costs_transport_network",
    "departure_datetime",
    "detailed_itineraries_bicycle",
    "detailed_itineraries_car",
    "detailed_itineraries_transit",
    "detailed_itineraries_walk",
    "gtfs_file_path",
    "gtfs_timezone_helsinki",
    "not_a_gtfs_file",
    "origin_point",
    "origins_invalid_duplicate_ids",
    "origins_invalid_no_id",
    "origins_valid_ids",
    "osm_pbf_file_path",
    "population_grid",
    "population_grid_points",
    "population_grid_points_first_three",
    "population_grid_points_four",
    "population_grid_points_second_three",
    "regional_task",
    "r5_jar_cached",
    "r5_jar_cached_invalid",
    "r5_jar_sha256",
    "r5_jar_sha256_github_error_message_when_posting",
    "r5_jar_sha256_invalid",
    "r5_jar_url",
    "sample_data_set_sha256",
    "sample_data_set_url",
    "snapped_population_grid_points",
    "transport_network",
    "transport_network_files_tuple",
    "transport_network_from_test_directory",
    "transport_network_from_test_files",
    "transport_network_from_test_files_without_gtfs",
    "unreachable_stops",
    "unsnappable_points",
    "walking_details_not_snapped",
    "walking_details_snapped",
    "walking_times_not_snapped",
    "walking_times_snapped",
]
