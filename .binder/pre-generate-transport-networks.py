#!/usr/bin/env python3

import r5py
import r5py.sampledata.helsinki
import r5py.sampledata.sao_paulo

_ = r5py.TransportNetwork(
    r5py.sampledata.helsinki.osm_pbf,
    [r5py.sampledata.helsinki.gtfs],
)
_ = r5py.TransportNetwork(
    r5py.sampledata.sao_paulo.osm_pbf,
    [r5py.sampledata.sao_paulo.gtfs],
)
