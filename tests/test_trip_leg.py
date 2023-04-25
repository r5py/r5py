#!/usr/bin/env python3

import datetime

import shapely

import r5py


class TestTripLeg:
    def test_repr(self):
        trip_leg = r5py.r5.trip_leg.TripLeg(
            r5py.TransportMode.TRANSIT,
            datetime.datetime(2023, 4, 25, 15, 30),
            12.67,
            datetime.timedelta(minutes=10),
            datetime.timedelta(minutes=2),
            "48A",
            shapely.LineString([[0, 0], [1, 1], [2, 2]])
        )
        assert repr(trip_leg) == "<TripLeg: TransportMode.TRANSIT, 12.67m, 600.0s, (0.0, 0.0) -> (2.0, 2.0)>"

    def test_add(self):
        trip_leg1 = r5py.r5.trip_leg.TripLeg(
            r5py.TransportMode.TRANSIT,
            datetime.datetime(2023, 4, 25, 15, 30),
            12.34,
            datetime.timedelta(minutes=10),
            datetime.timedelta(minutes=2),
            "56A",
            shapely.LineString([[0, 0], [1, 1], [2, 2]])
        )
        trip_leg2 = r5py.r5.trip_leg.TripLeg(
            r5py.TransportMode.TRANSIT,
            datetime.datetime(2023, 4, 25, 15, 30),
            98.76,
            datetime.timedelta(minutes=30),
            datetime.timedelta(minutes=5),
            "54A",
            shapely.LineString([[2, 2], [34, 34]])
        )

        trip = trip_leg1 + trip_leg2
        assert isinstance(trip, r5py.r5.trip.Trip)
        assert trip.legs == [trip_leg1, trip_leg2]

        trip = trip_leg2 + trip_leg1
        assert isinstance(trip, r5py.r5.trip.Trip)
        assert trip.legs == [trip_leg2, trip_leg1]

        trip = sum([trip_leg1, trip_leg2])
        assert isinstance(trip, r5py.r5.trip.Trip)
        assert trip.legs == [trip_leg1, trip_leg2]

        trip = r5py.r5.trip.Trip([trip_leg1])
        trip += trip_leg2
        assert isinstance(trip, r5py.r5.trip.Trip)
        assert trip.legs == [trip_leg1, trip_leg2]

        trip = r5py.r5.trip.Trip([trip_leg1])
        trip = trip_leg2 + trip
        assert isinstance(trip, r5py.r5.trip.Trip)
        assert trip.legs == [trip_leg2, trip_leg1]

    def test_as_table_row(self):
        trip_leg = r5py.r5.trip_leg.TripLeg(
            r5py.TransportMode.TRANSIT,
            datetime.datetime(2023, 4, 25, 15, 30),
            12.67,
            datetime.timedelta(minutes=10),
            datetime.timedelta(minutes=2),
            "48A",
            shapely.LineString([[0, 0], [1, 1], [2, 2]])
        )
        assert trip_leg.as_table_row() == [
            r5py.TransportMode.TRANSIT,
            datetime.datetime(2023, 4, 25, 15, 30),
            12.67,
            datetime.timedelta(minutes=10),
            datetime.timedelta(minutes=2),
            "48A",
            shapely.LineString([[0, 0], [1, 1], [2, 2]])
        ]
