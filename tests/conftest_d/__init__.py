#!/usr/bin/env python3


"""Fixtures to be used in r5py tests."""

# geopandas 1.0.1 imports shapely.geos which raises
# a Deprecation warning in Shapely 2.1.0
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        message=".*shapely.geos.*deprecated.*",
    )
    import geopandas  # noqa: F401


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
    broken_gtfs_file_path,
    cache_directory,
    elevation_model_file_path,
    gtfs_file_path,
    gtfs_timezone_helsinki,
    helsinki_osm_pbf_file_path,
    not_a_gtfs_file,
    sao_paulo_osm_pbf_file_path,
    transport_network,
    transport_network_checksum,
    transport_network_files_tuple,
    transport_network_from_test_directory,
    transport_network_from_test_files,
    transport_network_from_test_files_without_gtfs,
)

from .upstream_r5 import (
    can_compute_detailed_route_geometries,
)

__all__ = [
    "broken_gtfs_file_path",
    "cache_directory",
    "can_compute_detailed_route_geometries",
    "departure_datetime",
    "detailed_itineraries_bicycle",
    "detailed_itineraries_car",
    "detailed_itineraries_transit",
    "detailed_itineraries_walk",
    "elevation_model_file_path",
    "file_digest_blake2b",
    "file_digest_blake2s",
    "file_digest_sha256",
    "file_digest_test_file_as_pathlib_path",
    "file_digest_test_file_as_str",
    "gtfs_file_path",
    "gtfs_timezone_helsinki",
    "helsinki_osm_pbf_file_path",
    "isochrones_bicycle",
    "isochrones_car",
    "isochrones_from_multiple_origins",
    "isochrones_transit",
    "isochrones_walk",
    "java_garbage_collection",
    "multiple_origins",
    "not_a_gtfs_file",
    "origin_point",
    "origins_invalid_duplicate_ids",
    "origins_invalid_no_id",
    "origins_valid_ids",
    "population_grid",
    "population_grid_points",
    "population_grid_points_first_three",
    "population_grid_points_four",
    "population_grid_points_second_three",
    "r5_jar_cached",
    "r5_jar_cached_invalid",
    "r5_jar_sha256",
    "r5_jar_sha256_github_error_message_when_posting",
    "r5_jar_sha256_invalid",
    "r5_jar_url",
    "regional_task",
    "sample_data_set_sha256",
    "sample_data_set_url",
    "sao_paulo_osm_pbf_file_path",
    "snapped_population_grid_points",
    "transport_network",
    "transport_network_checksum",
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
