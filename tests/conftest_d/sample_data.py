#!/usr/bin/env python3


"""Fixtures related to testing the SampleData class."""


import pytest


SAMPLE_DATA_SET_URL = "https://raw.githubusercontent.com/r5py/r5py.sampledata.sao_paulo/main/data/spo_hexgrid.csv"
SAMPLE_DATA_SET_SHA256 = (
    "769660f8f1bc95d2741bbc4225e5e0e77e73461ea8b3e225a58e397b0748bdd4"
)


@pytest.fixture
def sample_data_set_sha256():
    """Return the SHA256 hash of the sample data at `sample_data_set_url()`."""
    yield SAMPLE_DATA_SET_SHA256


@pytest.fixture
def sample_data_set_url():
    """Return the web address from which a sample data set can be downloaded."""
    yield SAMPLE_DATA_SET_URL
