#!/usr/bin/env python3


import pathlib

import jpype

import r5py.util


class TestJavaCasting:
    def test_if_start_jvm_works_without_libjsig(self, monkeypatch):
        def _glob(*args, **kwargs):
            raise StopIteration

        monkeypatch.setattr(pathlib.Path, "glob", _glob)

        r5py.util.start_jvm()

    def test_shutdown_hook(self):
        r5py.util.start_jvm()
        jpype.shutdownJVM()
