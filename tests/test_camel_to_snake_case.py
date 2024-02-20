#!/usr/bin/env python3


import pytest

import r5py.util


class TestCamelToSnakeCase:
    @pytest.mark.parametrize(
        ["camel_case", "snake_case"],
        [
            ("camelCase", "camel_case"),
            ("CamelCase", "camel_case"),
            ("getHTTPResponseCode", "get_http_response_code"),
            ("HTTPResponseCodeXYZ", "http_response_code_xyz"),
        ],
    )
    def test_case_camel_case(self, camel_case, snake_case):
        assert r5py.util.camel_to_snake_case(camel_case) == snake_case
