#!/usr/bin/env python3

"""Location of custom errors."""


class NoIDColumnError(Exception):
    pass


class NonUniqueIDError(Exception):
    pass
