#!/usr/bin/env python3


"""Convert Python dicts to Java HashMaps."""


import jpype
import numpy

from .jvm import start_jvm


__all__ = ["JHashMap"]


start_jvm()


class JHashMap:
    """Cast a Python dict to a Java HashMap."""

    def __new__(cls, dict_):
        """Cast a Python dict to a Java HashMap."""
        key_types = list(set([type(key) for key in dict_.keys()]))
        if len(key_types) > 1:
            raise ValueError(f"All keys of an {cls.__name__} must be of same type")
        key_type = key_types[0]
        if key_type in [
            int,
            numpy.integer,
            numpy.int8,
            numpy.int16,
            numpy.int32,
            numpy.int64,
        ]:
            key_type = jpype.JLong
        elif key_type in [
            float,
            numpy.floating,
            numpy.float16,
            numpy.float32,
            numpy.float64,
            # numpy.float128,
        ]:
            key_type = jpype.JDouble
        elif key_type == str:
            key_type = jpype.JString
        else:
            raise ValueError(
                "Keys of _JHashMap can only be int, float, or str, "
                "or the numpy equivalents."
            )

        value_types = list(set([type(value) for value in dict_.values()]))
        if len(value_types) > 1:
            raise ValueError(f"All values of a {cls.__name__} must be of same type")
        value_type = value_types[0]
        if value_type in [
            int,
            numpy.integer,
            numpy.int8,
            numpy.int16,
            numpy.int32,
            numpy.int64,
        ]:
            value_type = jpype.JLong
        elif value_type in [
            float,
            numpy.floating,
            numpy.float16,
            numpy.float32,
            numpy.float64,
            # numpy.float128,
        ]:
            value_type = jpype.JDouble
        elif value_type == str:
            value_type = jpype.JString
        else:
            raise ValueError(
                "Values of _JHashMap can only be int, float, or str, "
                "or the numpy equivalents."
            )

        hashmap = jpype.JClass("java.util.HashMap")()
        for key, value in dict_.items():
            hashmap.put(key_type(key), value_type(value))

        return hashmap
