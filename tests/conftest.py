#!/usr/bin/env python3


import pytest
import pathlib
import sys



sys.path.insert(0, pathlib.Path().absolute().parent / "src")


@pytest.fixture(scope="session", autouse=True)
def disable_faulthandler():
    # jpype/jvm do not go along well with pytest
    import faulthandler
    faulthandler.enable()
    faulthandler.disable()
