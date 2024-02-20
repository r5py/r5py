#!/usr/bin/env python3


import pytest

import r5py
import com.conveyal.r5


class TestTransportMode:
    @pytest.mark.parametrize(
        ["enum_member", "enum_name", "java_type"],
        [
            (r5py.TransportMode.AIR, "AIR", com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.BUS, "BUS", com.conveyal.r5.api.util.TransitModes),
            (
                r5py.TransportMode.CABLE_CAR,
                "CABLE_CAR",
                com.conveyal.r5.api.util.TransitModes,
            ),
            (r5py.TransportMode.FERRY, "FERRY", com.conveyal.r5.api.util.TransitModes),
            (
                r5py.TransportMode.FUNICULAR,
                "FUNICULAR",
                com.conveyal.r5.api.util.TransitModes,
            ),
            (r5py.TransportMode.RAIL, "RAIL", com.conveyal.r5.api.util.TransitModes),
            (
                r5py.TransportMode.SUBWAY,
                "SUBWAY",
                com.conveyal.r5.api.util.TransitModes,
            ),
            (r5py.TransportMode.TRAM, "TRAM", com.conveyal.r5.api.util.TransitModes),
            (
                r5py.TransportMode.TRANSIT,
                "TRANSIT",
                com.conveyal.r5.api.util.TransitModes,
            ),
            (r5py.TransportMode.BICYCLE, "BICYCLE", com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.CAR, "CAR", com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.WALK, "WALK", com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.BICYCLE, "BICYCLE", com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.CAR, "CAR", com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.WALK, "WALK", com.conveyal.r5.api.util.LegMode),
            (
                r5py.TransportMode.BICYCLE_RENT,
                "BICYCLE_RENT",
                com.conveyal.r5.api.util.LegMode,
            ),
            (r5py.TransportMode.CAR_PARK, "CAR_PARK", com.conveyal.r5.api.util.LegMode),
        ],
    )
    def test_transportmode(self, enum_member, enum_name, java_type):
        assert enum_member.name == enum_name
        assert enum_member.name == java_type.valueOf(enum_name).name()

    @pytest.mark.parametrize(
        ["str_transport_mode", "expected_transport_mode"],
        [
            ("AIR", r5py.TransportMode.AIR),
            ("BUS", r5py.TransportMode.BUS),
            ("CABLE_CAR", r5py.TransportMode.CABLE_CAR),
            ("FERRY", r5py.TransportMode.FERRY),
            ("FUNICULAR", r5py.TransportMode.FUNICULAR),
            ("GONDOLA", r5py.TransportMode.GONDOLA),
            ("RAIL", r5py.TransportMode.RAIL),
            ("SUBWAY", r5py.TransportMode.SUBWAY),
            ("TRAM", r5py.TransportMode.TRAM),
            ("TRANSIT", r5py.TransportMode.TRANSIT),
            ("BICYCLE", r5py.TransportMode.BICYCLE),
            ("CAR", r5py.TransportMode.CAR),
            ("WALK", r5py.TransportMode.WALK),
            ("BICYCLE_RENT", r5py.TransportMode.BICYCLE_RENT),
            ("CAR_PARK", r5py.TransportMode.CAR_PARK),
            ("air", r5py.TransportMode.AIR),
            ("bus", r5py.TransportMode.BUS),
            ("cable_car", r5py.TransportMode.CABLE_CAR),
            ("ferry", r5py.TransportMode.FERRY),
            ("funicular", r5py.TransportMode.FUNICULAR),
            ("gondola", r5py.TransportMode.GONDOLA),
            ("rail", r5py.TransportMode.RAIL),
            ("subway", r5py.TransportMode.SUBWAY),
            ("tram", r5py.TransportMode.TRAM),
            ("transit", r5py.TransportMode.TRANSIT),
            ("bicycle", r5py.TransportMode.BICYCLE),
            ("car", r5py.TransportMode.CAR),
            ("walk", r5py.TransportMode.WALK),
            ("bicycle_rent", r5py.TransportMode.BICYCLE_RENT),
            ("car_park", r5py.TransportMode.CAR_PARK),
            ("AiR", r5py.TransportMode.AIR),
            ("bUs", r5py.TransportMode.BUS),
            ("CaBlE_CaR", r5py.TransportMode.CABLE_CAR),
            ("fErRy", r5py.TransportMode.FERRY),
            ("FuNiCuLaR", r5py.TransportMode.FUNICULAR),
            ("gOnDoLa", r5py.TransportMode.GONDOLA),
            ("RaIl", r5py.TransportMode.RAIL),
            ("SuBwAy", r5py.TransportMode.SUBWAY),
            ("TrAm", r5py.TransportMode.TRAM),
            ("TrAnSiT", r5py.TransportMode.TRANSIT),
            ("bIcYcLe", r5py.TransportMode.BICYCLE),
            ("CaR", r5py.TransportMode.CAR),
            ("wAlK", r5py.TransportMode.WALK),
            ("bIcYcLe_ReNt", r5py.TransportMode.BICYCLE_RENT),
            ("CaR_PaRk", r5py.TransportMode.CAR_PARK),
        ],
    )
    def test_str_transportmode(self, str_transport_mode, expected_transport_mode):
        assert r5py.TransportMode(str_transport_mode) == expected_transport_mode

    @pytest.mark.parametrize(
        ["invalid_transport_mode"],
        [
            ("Helicopter",),
            ("adsffoobar",),
            (13,),
            (None,),
            ("1234",),
        ],
    )
    def test_invalid_transportmode(self, invalid_transport_mode):
        with pytest.raises(ValueError, match="is not a valid TransportMode"):
            _ = r5py.TransportMode(invalid_transport_mode)

    @pytest.mark.parametrize(
        ["mode", "expected"],
        [
            ("CAR", True),
            ("BICYCLE", True),
            (r5py.TransportMode.WALK, True),
            (r5py.TransportMode.BICYCLE_RENT, True),
            (r5py.TransportMode.BUS, False),
            ("TRANSIT", False),
        ],
    )
    def test_is_leg_mode(self, mode, expected):
        assert r5py.TransportMode(mode).is_leg_mode == expected

    @pytest.mark.parametrize(
        ["mode", "expected"],
        [
            ("CAR", True),
            ("BICYCLE", True),
            (r5py.TransportMode.WALK, True),
            (r5py.TransportMode.BICYCLE_RENT, False),
            (r5py.TransportMode.BUS, False),
            ("TRANSIT", False),
        ],
    )
    def test_is_street_mode(self, mode, expected):
        assert r5py.TransportMode(mode).is_street_mode == expected

    @pytest.mark.parametrize(
        ["mode", "expected"],
        [
            ("CAR", False),
            ("BICYCLE", False),
            (r5py.TransportMode.WALK, False),
            (r5py.TransportMode.BICYCLE_RENT, False),
            (r5py.TransportMode.BUS, True),
            ("TRANSIT", True),
        ],
    )
    def test_is_transit_mode(self, mode, expected):
        assert r5py.TransportMode(mode).is_transit_mode == expected

    def test_add(self):
        transport_mode1 = r5py.TransportMode.TRANSIT
        transport_mode2 = r5py.TransportMode.WALK

        transport_modes = transport_mode1 + transport_mode2
        assert isinstance(transport_modes, list)
        assert transport_modes == [transport_mode1, transport_mode2]

        transport_modes = transport_mode2 + transport_mode1
        assert isinstance(transport_modes, list)
        assert transport_modes == [transport_mode2, transport_mode1]

        transport_modes = sum([transport_mode1, transport_mode2])
        assert isinstance(transport_modes, list)
        assert transport_modes == [transport_mode1, transport_mode2]

        transport_modes = [transport_mode1] + transport_mode2
        assert isinstance(transport_modes, list)
        assert transport_modes == [transport_mode1, transport_mode2]

        transport_modes = transport_mode1 + [transport_mode2]
        assert isinstance(transport_modes, list)
        assert transport_modes == [transport_mode1, transport_mode2]

    @pytest.mark.parametrize(
        ["invalid_other"],
        [
            (123.0,),
            (1,),
            ("asdfasdf",),
            ({},),
        ],
    )
    def test_add_invalid_type(self, invalid_other):
        transport_mode = r5py.TransportMode.TRANSIT
        with pytest.raises(TypeError, match="unsupported operand type"):
            _ = transport_mode + invalid_other

        with pytest.raises(TypeError, match="unsupported operand type"):
            _ = invalid_other + transport_mode
