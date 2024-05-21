#!/usr/bin/env python3


import pytest

import r5py.util


class TestSnakeToCamelCase:
    @pytest.mark.parametrize(
        ["snake_case", "camel_case"],
        [
            ("camel_case", "camelCase"),
            ("get_http_response_code", "getHttpResponseCode"),
            ("http_response_code_xyz", "httpResponseCodeXyz"),
            ("snake", "snake"),
        ],
    )
    def test_case_snake_case(self, snake_case, camel_case):
        assert r5py.util.snake_to_camel_case(snake_case) == camel_case
