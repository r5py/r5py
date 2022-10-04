#!/usr/bin/env python3


import pytest  # noqa: F401

import importlib
import os
import pathlib
import sys


class TestConfig:
    def test_os_environ_home(self):
        # unset $HOME
        del os.environ["HOME"]

        # unload all r5py modules:
        r5py_modules = list([module for module in sys.modules.keys() if module[:4] == "r5py"])
        for module in r5py_modules:
            sys.modules.pop(module)

        # also unload configargparse
        sys.modules.pop("configargparse")

        import configargparse
        from r5py.util import config
        assert config.CACHE_DIR == pathlib.Path("./.cache/r5py")
