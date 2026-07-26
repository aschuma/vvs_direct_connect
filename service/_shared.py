"""Formatting and predicate helpers reused by the trip services.

These helpers are pure functions with no I/O; they exist to keep the
:mod:`service.v1` and :mod:`service.v2` modules focused on the shape
of their respective responses rather than on low-level details.
"""

from __future__ import annotations

from datetime import datetime

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
    return all((
        leg.origin.planned is not None,
        leg.origin.estimated is not None,
        leg.destination.planned is not None,
        leg.destination.estimated is not None,
    ))
