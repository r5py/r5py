#!/usr/bin/env python3

import datetime

import pytest
import shapely

import r5py


class TestTrip:
    def test_str(self):
        trip_leg = r5py.r5.trip_leg.TripLeg(
            transport_mode=r5py.TransportMode.TRANSIT,
            departure_time=datetime.datetime(2023, 4, 25, 15, 30),
            distance=12.67,
            travel_time=datetime.timedelta(minutes=10),
            wait_time=datetime.timedelta(minutes=2),
            route_id="48A",
            geometry=shapely.LineString([[0, 0], [1, 1], [2, 2]]),
        )
        trip = r5py.r5.trip.Trip([trip_leg])
        assert (
            repr(trip)
            == "<Trip: 12.67m, 600.0s, <TripLeg: TransportMode.TRANSIT, 12.67m, 600.0s, (0.0, 0.0) -> (2.0, 2.0)>>"
        )

    def test_summarised_properties(self):
        trip_leg1 = r5py.r5.trip_leg.TripLeg(
            transport_mode=r5py.TransportMode.TRANSIT,
            departure_time=datetime.datetime(2023, 4, 25, 15, 30),
            distance=12.34,
            travel_time=datetime.timedelta(minutes=10),
            wait_time=datetime.timedelta(minutes=2),
            route_id="56A",
            geometry=shapely.LineString([[0, 0], [1, 1], [2, 2]]),
        )
        trip_leg2 = r5py.r5.trip_leg.TripLeg(
            transport_mode=r5py.TransportMode.TRANSIT,
            departure_time=datetime.datetime(2023, 4, 25, 15, 30),
            distance=98.76,
            travel_time=datetime.timedelta(minutes=30),
            wait_time=datetime.timedelta(minutes=5),
            route_id="54A",
            geometry=shapely.LineString([[2, 2], [34, 34]]),
        )

        trip = trip_leg1 + trip_leg2

        assert trip.distance == pytest.approx(111.10)
        assert trip.geometry.wkt == "LINESTRING (0 0, 1 1, 2 2, 34 34)"
        assert trip.route_ids == ["56A", "54A"]
        assert trip.transport_modes == [
            r5py.TransportMode.TRANSIT,
            r5py.TransportMode.TRANSIT,
        ]
        assert trip.travel_time == datetime.timedelta(minutes=(30 + 10))
        assert trip.wait_time == datetime.timedelta(minutes=(2 + 5))

    def test_as_table(self):
        trip_leg = r5py.r5.trip_leg.TripLeg(
            transport_mode=r5py.TransportMode.TRANSIT,
            departure_time=datetime.datetime(2023, 4, 25, 15, 30),
            distance=12.67,
            travel_time=datetime.timedelta(minutes=10),
            wait_time=datetime.timedelta(minutes=2),
            feed="GTFS",
            agency_id="HSR",
            route_id="48A",
            start_stop_id="90210",
            end_stop_id="10802",
            geometry=shapely.LineString([[0, 0], [1, 1], [2, 2]]),
        )
        trip = r5py.r5.trip.Trip([trip_leg])

        assert trip.as_table() == [
            [
                0,
                r5py.TransportMode.TRANSIT,
                datetime.datetime(2023, 4, 25, 15, 30),
                12.67,
                datetime.timedelta(minutes=10),
                datetime.timedelta(minutes=2),
                "GTFS",
                "HSR",
                "48A",
                "90210",
                "10802",
                shapely.LineString([[0, 0], [1, 1], [2, 2]]),
            ]
        ]

    def test_distance_none(self):
        trip = sum(
            [
                r5py.r5.trip_leg.TripLeg(distance=None),
                r5py.r5.trip_leg.TripLeg(distance=None),
            ]
        )
        assert trip.distance is None
