#!/usr/bin/env python3


import pytest

import r5py
import com.conveyal.r5


class TestBreakdownStat:
    @pytest.mark.parametrize(
        ["enum_member", "enum_name"],
        [
            (r5py.r5.BreakdownStat.MEAN, "MEAN"),
            (r5py.r5.BreakdownStat.MINIMUM, "MINIMUM"),
        ],
    )
    def test_breakdownstats(self, enum_member, enum_name):
        assert enum_member.name == enum_name
        assert isinstance(
            enum_member.value, com.conveyal.r5.analyst.cluster.PathResult.Stat
        )
        assert (
            enum_member.value
            == com.conveyal.r5.analyst.cluster.PathResult.Stat.valueOf(enum_name)
        )
        assert (
            enum_member.name
            == com.conveyal.r5.analyst.cluster.PathResult.Stat.valueOf(enum_name).name()
        )
