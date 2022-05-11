#!/usr/bin/env python3

"""Convert a camelCase/CamelCase formated string to a snake_case format."""


import re


__all__ = ["camel_to_snake_case"]


# https://stackoverflow.com/a/1176023


CAMEL_CASE_TO_SNAKE_CASE_RE1 = re.compile("(.)([A-Z][a-z]+)")
CAMEL_CASE_TO_SNAKE_CASE_RE2 = re.compile("([a-z0-9])([A-Z])")
CAMEL_CASE_TO_SNAKE_CASE_SUBSTITUTE = r"\1_\2"


def camel_to_snake_case(camel_case):
    """Convert `camel_case` to snake_case spelling."""
    return CAMEL_CASE_TO_SNAKE_CASE_RE2.sub(
        CAMEL_CASE_TO_SNAKE_CASE_SUBSTITUTE,
        CAMEL_CASE_TO_SNAKE_CASE_RE1.sub(
            CAMEL_CASE_TO_SNAKE_CASE_SUBSTITUTE, camel_case
        ),
    ).lower()
