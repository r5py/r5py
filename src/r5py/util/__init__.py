#!/usr/bin/env python3

"""Utility functions, e.g., starting a JVM, and accessing configuration."""

from .jvm import start_jvm
from .camel_to_snake_case import camel_to_snake_case
from .config import Config
from .contains_gtfs_data import contains_gtfs_data
from .data_validation import check_od_data_set
from .good_enough_equidistant_crs import GoodEnoughEquidistantCrs
from .parse_int_date import parse_int_date
from .snake_to_camel_case import snake_to_camel_case
# from .custom_cost_conversions import (
#     convert_python_dict_to_java_hashmap,
#     convert_custom_cost_data_to_custom_cost_instance,
#     convert_custom_cost_instances_to_java_list,
# )
# from .exceptions import CustomCostDataError, CustomCostConversionError

__all__ = [
    "start_jvm",
    "camel_to_snake_case",
    "check_od_data_set",
    "Config",
    "contains_gtfs_data",
    "GoodEnoughEquidistantCrs",
    "parse_int_date",
    "snake_to_camel_case",
    "custom_cost_conversions",
    # "convert_python_dict_to_java_hashmap",
    # "convert_custom_cost_data_to_custom_cost_instance",
    # "convert_custom_cost_instances_to_java_list",
    # "CustomCostDataError",
    # "CustomCostConversionError",
]
