"""HTTP client and parser for the VVS EFA trip-planning endpoint.

VVS (Verkehrs- und Tarifverbund Stuttgart) exposes a public EFA
(Elektronische Fahrplanauskunft) endpoint that returns JSON when the
``outputFormat=rapidJSON`` query parameter is set. This module wraps
that endpoint and translates its response into a small set of
immutable value objects.

Response shape at a glance::

    {
      "journeys": [
        {
          "legs": [
            {
              "origin":         { "id", "name",
                                  "departureTimePlanned",
                                  "departureTimeEstimated", ... },
              "destination":    { "id", "name",
                                  "arrivalTimePlanned",
                                  "arrivalTimeEstimated", ... },
              "transportation": { "number", ... }
            },
            ...
          ]
        },
        ...
      ]
    }

Each ``journey`` becomes a :class:`Trip`, each ``leg`` becomes a
:class:`Leg`, and ``origin`` / ``destination`` become :class:`Stop`\\ s.

Public API
----------
* :func:`fetch_trips` -- perform the HTTP request and return parsed trips.
* :func:`parse_response` -- parse an already-decoded EFA payload
  (useful for tests and offline processing).
* :class:`Trip`, :class:`Leg`, :class:`Stop` -- immutable value objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Final, Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import logging

__all__ = ["Stop", "Leg", "Trip", "fetch_trips", "parse_response"]

API_URL: Final[str] = "https://www3.vvs.de/mngvvs/XML_TRIP_REQUEST2"
DEFAULT_TIMEOUT_SECONDS: Final[float] = 10.0

_logger = logging.getLogger(__name__)

# Constant EFA request parameters. Values that depend on the caller
# (station ids and the ``check_time``) are merged on top of this
# baseline in :func:`_build_url`. The values are the ones the VVS web
# frontend itself sends and are the minimum set required to obtain a
# usable rapidJSON response.
_BASE_PARAMS: Final[Mapping[str, str]] = {
    "SpEncId": "0",
    "calcOneDirection": "1",
    "changeSpeed": "normal",
    "computationType": "sequence",
    "coordOutputFormat": "EPSG:4326",
    "cycleSpeed": "14",
    "deleteAssignedStops": "0",
    "deleteITPTWalk": "0",
    "descWithElev": "1",
    "illumTransfer": "on",
    "imparedOptionsActive": "1",
    "itOptionsActive": "1",
    "language": "de",
    "locationServerActive": "1",
    "macroWebTrip": "true",
    "noElevationProfile": "1",
    "noElevationSummary": "1",
    "outputFormat": "rapidJSON",
    "outputOptionsActive": "1",
    "ptOptionsActive": "1",
    "routeType": "leasttime",
    "searchLimitMinutes": "360",
    "securityOptionsActive": "1",
    "serverInfo": "1",
    "showInterchanges": "1",
    "trITArrMOT": "100",
    "trITArrMOTvalue": "15",
    "trITDepMOT": "100",
    "trITDepMOTvalue": "15",
    "tryToFindLocalityStops": "1",
    "type_destination": "any",
    "type_origin": "any",
    "useElevationData": "1",
    "useLocalityMainStop": "0",
    "useRealtime": "1",
    "useUT": "1",
    "version": "10.2.10.139",
    "w_objPrefAl": "12",
    "w_regPrefAm": "1",
}

# A station may be identified by its numeric or textual VVS id, or by
# an ``Enum`` member whose ``value`` carries that id.
StationId = str | int | Enum


# --------------------------------------------------------------------------- #
# Value objects
# --------------------------------------------------------------------------- #

@dataclass(frozen=True, slots=True)
class Stop:
    """A station stop annotated with the times a transport calls at it.

    Attributes
    ----------
    id:
        VVS station id (e.g. ``"de:08111:6118"``). ``None`` if absent.
    name:
        Human-readable station name (e.g. ``"Stuttgart Hauptbahnhof"``).
    planned:
        Scheduled departure or arrival time.
    estimated:
        Real-time-updated departure or arrival time. Equal to
        :attr:`planned` when no real-time data is available.
    """

    id: str | None
    name: str | None
    planned: datetime | None
    estimated: datetime | None


@dataclass(frozen=True, slots=True)
class Leg:
    """A single, uninterrupted section of a journey.

    A leg starts at :attr:`origin`, ends at :attr:`destination` and is
    served by one line (``line_number`` such as ``"S1"`` or ``"U6"``).
    A leg with ``line_number is None`` represents a walking transfer
    inserted by the router.
    """

    origin: Stop
    destination: Stop
    line_number: str | None


@dataclass(frozen=True, slots=True)
class Trip:
    """A full journey from one station to another.

    A trip consists of one or more :class:`Leg`\\ s. A direct
    connection has exactly one leg; interchange journeys have several.
    """

    legs: tuple[Leg, ...]


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def _parse_iso_z(value: str | None) -> datetime | None:
    """Parse an EFA UTC timestamp of the form ``YYYY-MM-DDTHH:MM:SSZ``.

    Returns ``None`` for missing or empty input so callers can decide
    how to react to legs that carry no timing information.
    """
    if not value:
        return None
    return datetime.strptime(value.removesuffix("Z"), "%Y-%m-%dT%H:%M:%S")


def _parse_stop(raw: Mapping[str, Any] | None, time_key_prefix: str) -> Stop:
    """Turn a raw ``origin`` or ``destination`` object into a :class:`Stop`.

    Parameters
    ----------
    raw:
        The raw dict for either ``origin`` or ``destination``. May be
        ``None`` -- an empty :class:`Stop` is returned in that case.
    time_key_prefix:
        Either ``"departure"`` (for the origin) or ``"arrival"`` (for
        the destination). Selects which pair of timing fields to read
        (``departureTimePlanned`` / ``departureTimeEstimated`` vs.
        ``arrivalTimePlanned`` / ``arrivalTimeEstimated``).
    """
    raw = raw or {}
    return Stop(
        id=raw.get("id"),
        name=raw.get("name"),
        planned=_parse_iso_z(raw.get(f"{time_key_prefix}TimePlanned")),
        estimated=_parse_iso_z(raw.get(f"{time_key_prefix}TimeEstimated")),
    )


def _parse_leg(raw: Mapping[str, Any]) -> Leg:
    """Turn a raw ``leg`` object into a :class:`Leg`."""
    return Leg(
        origin=_parse_stop(raw.get("origin"), "departure"),
        destination=_parse_stop(raw.get("destination"), "arrival"),
        line_number=(raw.get("transportation") or {}).get("number"),
    )


def parse_response(payload: Mapping[str, Any] | None, limit: int) -> list[Trip]:
    """Extract up to ``limit`` trips from a decoded EFA JSON payload.

    Parameters
    ----------
    payload:
        The decoded JSON body returned by the EFA endpoint, or ``None``
        (which yields an empty list).
    limit:
        Maximum number of trips to return. Any excess journeys in the
        payload are discarded.
    """
    journeys = (payload or {}).get("journeys") or []
    return [
        Trip(legs=tuple(_parse_leg(leg) for leg in journey.get("legs") or []))
        for journey in journeys[:limit]
    ]


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #

def _station_value(station: StationId) -> str:
    """Normalise a station identifier to the string form the API expects."""
    return str(station.value if isinstance(station, Enum) else station)


def _build_url(
    origin: StationId, destination: StationId, check_time: datetime
) -> str:
    """Assemble the fully-encoded EFA request URL for a trip lookup.

    ``check_time`` is split into the API's ``itdDate`` (``YYYYMMDD``)
    and ``itdTime`` (``HHMM``) parameters.
    """
    params = {
        **_BASE_PARAMS,
        "itdDate": check_time.strftime("%Y%m%d"),
        "itdTime": check_time.strftime("%H%M"),
        "name_origin": _station_value(origin),
        "name_destination": _station_value(destination),
    }
    return f"{API_URL}?{urlencode(params)}"


def fetch_trips(
    origin_station_id: StationId,
    destination_station_id: StationId,
    *,
    check_time: datetime | None = None,
    limit: int = 100,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> list[Trip]:
    """Query the VVS EFA endpoint and return the parsed trips.

    Parameters
    ----------
    origin_station_id:
        Departure station identifier.
    destination_station_id:
        Arrival station identifier.
    check_time:
        Point in time to plan for. Defaults to :func:`datetime.now`.
    limit:
        Maximum number of trips to return.
    timeout:
        HTTP request timeout in seconds.

    Raises
    ------
    RuntimeError:
        If the EFA endpoint responds with a non-200 status code.
    urllib.error.URLError:
        For network-level failures.
    json.JSONDecodeError:
        If the response body is not valid JSON.
    """
    url = _build_url(
        origin_station_id,
        destination_station_id,
        check_time or datetime.now(),
    )
    request = Request(url, headers={"Accept": "application/json"})

    from urllib.error import HTTPError

    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise RuntimeError(f"VVS API returned HTTP {response.status}")
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"VVS API returned HTTP {exc.code}") from exc
    _logger.debug("VVS API returned %d journey(s)", len(payload.get("journeys") or []))
    return parse_response(payload, limit)
