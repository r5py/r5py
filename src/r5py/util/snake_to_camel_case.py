#!/usr/bin/env python3

"""Convert a snack_case formated string to a camelCase format."""


__all__ = ["snake_to_camel_case"]


def snake_to_camel_case(snake_case):
    """Convert `snake_case` to camelCase spelling."""
    if "_" in snake_case:
        words = snake_case.split("_")
        words = [words[0].lower()] + [word.title() for word in words[1:]]
        camel_case = "".join(words)
    else:
        camel_case = snake_case[0].lower() + snake_case[1:]
    return camel_case
