#!/usr/bin/env python3

"""Parse an integer date value (as return by com.conveyal.gtfs.GtfsFeed.services.end_date)."""


import datetime


__all__ = ["parse_int_date"]


def parse_int_date(int_date):
    """
    Parse an integer date value.

    com.conveyal.gtfs.GtfsFeed.services.start_date and .end_date are integer
    values in the format YYYYMMDD, so, e.g., 20220222 for 2 February 2022.
    This function converts such an integer value into the respective
    datetime.datetime (at 0:00 o’clock).

    """
    year = round(int_date / 10000)
    month = round((int_date % 10000) / 100)
    day = int_date % 100

    return datetime.datetime(year, month, day)
