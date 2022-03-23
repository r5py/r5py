#!/usr/bin/env python3

"""Cast Python enums to Java EnumSets."""

import enum

from . import config, jvm  # noqa: F401


__all__ = ["JavaEnum"]


class JavaEnum(enum.Enum):
    # def _generate_next_value_(name, start, count, last_values):

    def __new__(cls, label):
        print(cls, cls.__class__.__name__, cls.__members__, dir(cls))
        print(cls.__java_parent)
        obj = object.__new__(cls)
        obj.label = label
        obj._value_ = cls.__java_parent.valueOf(label)
        return obj

    def _missing_(cls, value):
        print(cls, value)
        return value

# @jpype._jcustomizer.JConversion(
#     "java.util.EnumSet",
#     instanceof=enum.EnumMeta
# )
# def _cast_EnumMeta(java_class, object_):
#     try:
#         return jpype._jclass.JClass(object_._java_class)
#     except AttributeError:
#         raise TypeError(
#             "Could not cast enum {} to java.util.EnumSet".format(
#                 object_.__class__.__name__
#             )
#         )
