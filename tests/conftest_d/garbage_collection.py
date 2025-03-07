#!/usr/bin/env python3


"""An auto-use fixture that calls Java garbage collection before every function."""


import jpype
import pytest


@pytest.fixture(autouse=True, scope="function")
def java_garbage_collection():
    """Call Java GC before every function."""
    jpype.java.lang.System.gc()
