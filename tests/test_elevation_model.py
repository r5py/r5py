#!/usr/bin/env python3


import r5py


class Test_ElevationModel:
    def test_init_with_single_dem(
        self,
        elevation_model_file_path,
    ):
        _ = r5py.r5.elevation_model.ElevationModel(elevation_model_file_path)

    def test_init_with_single_dem_list(
        self,
        elevation_model_file_path,
    ):
        _ = r5py.r5.elevation_model.ElevationModel([elevation_model_file_path])

    def test_init_with_multiple_dem_list(
        self,
        elevation_model_file_path,
        elevation_model_sample_file_path,
    ):
        _ = r5py.r5.elevation_model.ElevationModel(
            [elevation_model_file_path, elevation_model_sample_file_path]
        )
