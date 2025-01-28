#!/usr/bin/env python3

"""Configuration and fixtures for testing r5py."""

# This is a init file common to all tests. It is automatically sourced
# by pytest et al.

# This file imports all files in the conftest.d directory

# Define common constants (e.g., paths to test data) and fixtures (e.g.,
# transport network) there and import the fixtures into conftest_d/__init__.py.

from .conftest_d import *  # noqa: F401,F403
