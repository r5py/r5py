#!/usr/bin/env python3


"""Fixtures to be used in r5py tests."""


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

from .file_digest import (
    file_digest_test_file_as_pathlib_path,
    file_digest_test_file_as_str,
    file_digest_sha256,
    file_digest_blake2b,
    file_digest_blake2s,
)

from .garbage_collection import java_garbage_collection

from .origins import (
    multiple_origins,
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
    isochrones_from_multiple_origins,
    isochrones_bicycle,
    isochrones_car,
    isochrones_transit,
    isochrones_walk,
    travel_times_bicycle,
    travel_times_car,
    travel_times_transit,
    travel_times_walk,
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

from .upstream_r5 import (
    can_compute_detailed_route_geometries,
)

__all__ = [
    "can_compute_detailed_route_geometries",
    "departure_datetime",
    "detailed_itineraries_bicycle",
    "detailed_itineraries_car",
    "detailed_itineraries_transit",
    "detailed_itineraries_walk",
    "file_digest_test_file_as_pathlib_path",
    "file_digest_test_file_as_str",
    "file_digest_sha256",
    "file_digest_blake2b",
    "file_digest_blake2s",
    "java_garbage_collection",
    "gtfs_file_path",
    "gtfs_timezone_helsinki",
    "isochrones_from_multiple_origins",
    "isochrones_bicycle",
    "isochrones_car",
    "isochrones_transit",
    "isochrones_walk",
    "multiple_origins",
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
    "travel_times_bicycle",
    "travel_times_car",
    "travel_times_transit",
    "travel_times_walk",
    "unreachable_stops",
    "unsnappable_points",
    "walking_details_not_snapped",
    "walking_details_snapped",
    "walking_times_not_snapped",
    "walking_times_snapped",
]
