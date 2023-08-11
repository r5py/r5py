#!/usr/bin/env python3


import importlib
import os

import r5py.util.config


class TestConfig:
    def test_setdefaulthome(self):
        del os.environ["HOME"]
        importlib.reload(r5py.util.config)
        assert os.environ["HOME"] == "."
