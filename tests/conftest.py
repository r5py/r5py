#!/usr/bin/env python3


import pytest


@pytest.fixture(scope="session", autouse=True)
def disable_faulthandler():
    # jpype/jvm do not go along well with pytest
    import faulthandler
    faulthandler.enable()
    faulthandler.disable()
