"""Trip lookup supporting multi-leg (interchange) journeys.

Exposes :func:`find_trips`, which queries the VVS EFA endpoint and
returns all journeys that contain at least one transport leg. Walking
transfers inserted by the router are removed so that each response
trip only references legs served by an actual line.

Each returned trip is a JSON-serialisable ``dict`` suitable for the
``/api/v2/`` endpoint. It carries both an aggregated view (overall
departure, arrival, travel time, comma-joined line numbers) and a
per-leg breakdown under the ``details`` key.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from service._shared import (
    has_line_number,
    is_fully_timed,
    iso_ts,
    minutes_between,
    to_success_response,
)
from service.vvs_client import Leg, Trip, fetch_trips


def _leg_detail(leg: Leg) -> dict[str, Any]:
    """Shape a single leg for the ``details`` array of the v2 response.

    Each detail entry reflects the timing of its own leg, so an
    interchange journey shows realistic departure/arrival times for
    every line involved.
    """
    origin, destination = leg.origin, leg.destination
    return {
        "from": origin.name,
        "from_id": origin.id,
        "to": destination.name,
        "to_id": destination.id,
        "number": leg.line_number,
        "departure_planned": iso_ts(origin.planned),
        "departure_estimated": iso_ts(origin.estimated),
        "arrival_planned": iso_ts(destination.planned),
        "arrival_estimated": iso_ts(destination.estimated),
    }


def _as_multi_leg_trip(legs: tuple[Leg, ...]) -> dict[str, Any]:
    """Shape a sequence of legs into the v2 response dict.

    The aggregated fields describe the journey end-to-end: they are
    derived from the origin of the first leg and the destination of
    the last one. ``number`` is the comma-joined list of line numbers
    in traversal order and ``numbers`` exposes the same list unjoined.
    ``details`` contains one entry per leg.
    """
    first_origin = legs[0].origin
    last_destination = legs[-1].destination
    line_numbers = [leg.line_number for leg in legs]

    return {
        "from_id": first_origin.id,
        "from": first_origin.name,
        "to_id": last_destination.id,
        "to": last_destination.name,
        "departure_planned": iso_ts(first_origin.planned),
        "departure_estimated": iso_ts(first_origin.estimated),
        "departure_delay": minutes_between(first_origin.estimated, first_origin.planned),
        "arrival_planned": iso_ts(last_destination.planned),
        "arrival_estimated": iso_ts(last_destination.estimated),
        "arrival_delay": minutes_between(last_destination.estimated, last_destination.planned),
        "travel_time": minutes_between(last_destination.estimated, first_origin.planned),
        "number": ",".join(line_numbers),
        "numbers": line_numbers,
        "details": [_leg_detail(leg) for leg in legs],
    }


def _transport_legs(trip: Trip) -> tuple[Leg, ...]:
    """Return the subset of ``trip``'s legs eligible for v2 shaping.

    Walking transfers inserted by the router (no line number) and
    legs with incomplete timing information are removed here so that
    downstream shaping only sees legs that can be rendered end-to-end
    without ``null`` values in the response.
    """
    return tuple(leg for leg in trip.legs if has_line_number(leg) and is_fully_timed(leg))


def find_trips(
    from_id: str,
    to_id: str,
    limit: int,
    check_time: datetime,
) -> dict[str, Any]:
    """Return multi-leg trips between two stations, enveloped.

    The return value is the full JSON body the ``/api/v2/`` endpoint
    serves: ``{"trips": [...], "status": 200}``. HTTP handlers only
    have to :func:`flask.jsonify` it.

    Parameters
    ----------
    from_id:
        Departure station id.
    to_id:
        Arrival station id.
    limit:
        Upper bound for the number of trips fetched from the EFA API.
        The number of returned trips may be lower once journeys with
        no transport leg have been discarded.
    check_time:
        Point in time to plan for.
    """
    trips = fetch_trips(from_id, to_id, check_time=check_time, limit=limit)
    return to_success_response([
        _as_multi_leg_trip(legs)
        for legs in (_transport_legs(trip) for trip in trips)
        if legs
    ])
