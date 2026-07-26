"""Formatting, predicate, and envelope helpers reused by the trip services.

These helpers are pure functions with no I/O; they exist to keep the
:mod:`service.v1` and :mod:`service.v2` modules focused on the shape
of their respective responses rather than on low-level details.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from service.vvs_client import Leg


def iso_ts(moment: datetime) -> str:
    """Format a UTC ``datetime`` as ``YYYY-MM-DDTHH:MM:SSZ``.

    The trailing ``Z`` marks the value as UTC, matching the format the
    VVS EFA API itself uses in its responses.
    """
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def minutes_between(later: datetime, earlier: datetime) -> int:
    """Return the whole minutes between two ``datetime``\\ s.

    Computes ``later - earlier`` and truncates toward zero. Typically
    used to derive a delay in minutes from a planned/estimated pair or
    a travel time from a departure/arrival pair.
    """
    return int((later - earlier).total_seconds() / 60)


def has_line_number(leg: Leg) -> bool:
    """Return ``True`` when ``leg`` is served by an actual transport line.

    Legs without a ``line_number`` are walking transfers inserted by
    the router; the v2 service filters them out because they have no
    meaningful line identifier to expose.
    """
    return leg.line_number is not None


def is_fully_timed(leg: Leg) -> bool:
    """Return ``True`` when both ends of ``leg`` carry planned and estimated times.

    The VVS EFA endpoint occasionally omits timing fields for legs in
    a planning-only state. The response envelope of this service
    cannot represent missing timestamps (every trip carries formatted
    strings and integer delays), so the trip-service layer drops such
    legs before shaping to avoid ``AttributeError`` /
    ``TypeError`` on ``None``.
    """
    return all(
        t is not None
        for stop in (leg.origin, leg.destination)
        for t in (stop.planned, stop.estimated)
    )


def to_success_response(trips: list[dict[str, Any]]) -> dict[str, Any]:
    """Wrap a list of shaped trips in the standard success envelope.

    The envelope is ``{"trips": [...], "status": 200}`` -- the shape
    every HTTP consumer sees on a successful trip lookup. Keeping the
    envelope in the service layer makes the response body a single
    concern owned by the service module: HTTP handlers only have to
    :func:`flask.jsonify` the returned dict.

    The mirror error envelope stays in the HTTP layer because it is
    tied to exception handling and HTTP status codes, which are not
    service concerns.
    """
    return {"trips": trips, "status": 200}
