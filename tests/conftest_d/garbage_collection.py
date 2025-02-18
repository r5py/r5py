#!/usr/bin/env python3


"""An auto-use fixture that calls Java garbage collection before every class."""


import jpype
import pytest


@pytest.fixture(autouse=True, scope="class")
def java_garbage_collection():
    """Call Java GC before every class."""
    jpype.java.lang.System.gc()
