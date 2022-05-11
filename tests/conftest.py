#!/usr/bin/env python3


import pytest
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
print(sys.path)


@pytest.fixture(scope="session", autouse=True)
def disable_faulthandler():
    # jpype/jvm do not go along well with pytest
    import faulthandler
    faulthandler.enable()
    faulthandler.disable()
