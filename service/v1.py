"""Trip lookup limited to direct (single-leg) connections.

Exposes :func:`find_trips`, which queries the VVS EFA endpoint and
returns only those journeys that consist of exactly one leg -- i.e.
no interchange, no walking transfer. Each returned trip is shaped as
a JSON-serialisable ``dict`` suitable for the ``/api/v1/`` endpoint.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from service._shared import is_fully_timed, iso_ts, minutes_between
from service.vvs_client import Leg, Trip, fetch_trips


def _as_direct_trip(leg: Leg) -> dict[str, Any]:
    """Shape a single leg into the v1 response dict.

    The returned dict carries the origin and destination identity,
    the planned and estimated departure/arrival timestamps, the
    corresponding delays in minutes, the total travel time and the
    line number serving the connection.
    """
    origin, destination = leg.origin, leg.destination
    return {
        "from_id": origin.id,
        "to_id": destination.id,
        "from": origin.name,
        "to": destination.name,
        "departure_planned": iso_ts(origin.planned),
        "departure_estimated": iso_ts(origin.estimated),
        "departure_delay": minutes_between(origin.estimated, origin.planned),
        "arrival_planned": iso_ts(destination.planned),
        "arrival_estimated": iso_ts(destination.estimated),
        "arrival_delay": minutes_between(destination.estimated, destination.planned),
        "travel_time": minutes_between(destination.estimated, origin.planned),
        "number": leg.line_number,
    }


def _is_direct(trip: Trip) -> bool:
    """Return ``True`` when ``trip`` consists of exactly one leg."""
    return len(trip.legs) == 1


def _is_shapeable(trip: Trip) -> bool:
    """Return ``True`` when ``trip`` can be rendered as a v1 response.

    A trip is shapeable when it consists of exactly one leg *and* that
    leg carries complete timing information on both endpoints. Legs
    with partial timing are dropped rather than serialised with
    ``null`` values, keeping the response schema consistent.
    """
    return _is_direct(trip) and is_fully_timed(trip.legs[0])


def find_trips(
    from_id: str,
    to_id: str,
    limit: int,
    check_time: datetime,
) -> list[dict[str, Any]]:
    """Return the direct connections between two stations.

    Parameters
    ----------
    from_id:
        Departure station id.
    to_id:
        Arrival station id.
    limit:
        Upper bound for the number of trips fetched from the EFA API.
        The number of returned direct trips may be lower once
        interchange journeys and trips with partial timing information
        have been filtered out.
    check_time:
        Point in time to plan for.
    """
    trips = fetch_trips(from_id, to_id, check_time=check_time, limit=limit)
    return [_as_direct_trip(trip.legs[0]) for trip in trips if _is_shapeable(trip)]
