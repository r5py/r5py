#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py.util


class TestCamelToSnakeCase:
    def test_case_camel_case(self):
        test_cases = {
            "camelCase": "camel_case",
            "CamelCase": "camel_case",
            "getHTTPResponseCode": "get_http_response_code",
            "HTTPResponseCodeXYZ": "http_response_code_xyz"
        }
        for input_value, expected_output_value in test_cases.items():
            assert r5py.util.camel_to_snake_case(input_value) == expected_output_value
