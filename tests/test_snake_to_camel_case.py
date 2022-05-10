#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py.util


class TestSnakeToCamelCase:
    def test_case_snake_case(self):
        test_cases = {
            "camel_case": "camelCase",
            "get_http_response_code": "getHttpResponseCode",
            "http_response_code_xyz": "httpResponseCodeXyz"
        }
        for input_value, expected_output_value in test_cases.items():
            assert r5py.util.snake_to_camel_case(input_value) == expected_output_value
