"""Tests for :mod:`service.v1` (direct-connection lookup)."""

from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from service import v1
from service.vvs_client import parse_response


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "trip_response.json"


def _canned_trips(limit: int) -> list:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return parse_response(payload, limit)


class FindTripsTest(unittest.TestCase):
    """``find_trips`` should return only single-leg journeys.

    Multi-leg (interchange) journeys are filtered out. A single-leg
    journey that happens to be a walking transfer (``number is None``)
    is still returned so that callers can decide how to handle it.
    """

    def test_multi_leg_journeys_are_filtered(self) -> None:
        with patch.object(
            v1, "fetch_trips", side_effect=lambda *a, **k: _canned_trips(k["limit"])
        ):
            trips = v1.find_trips("A", "B", limit=10, check_time=datetime(2026, 5, 1))

        # Fixture has 3 journeys: 1 direct-with-transport, 1 interchange
        # (3 legs), 1 walk-only (1 leg). The interchange journey is
        # dropped; the direct and walk-only single-leg trips remain.
        self.assertEqual(len(trips), 2)
        line_numbers = [t["number"] for t in trips]
        self.assertEqual(line_numbers, ["S1", None])

    def test_direct_trip_shape(self) -> None:
        with patch.object(
            v1, "fetch_trips", side_effect=lambda *a, **k: _canned_trips(k["limit"])
        ):
            trips = v1.find_trips("A", "B", limit=10, check_time=datetime(2026, 5, 1))

        trip = trips[0]
        self.assertEqual(trip["from"], "Stuttgart Hbf (tief)")
        self.assertEqual(trip["to"], "Esslingen (N)")
        self.assertEqual(trip["number"], "S1")
        self.assertEqual(trip["departure_planned"], "2026-05-01T10:00:00Z")
        self.assertEqual(trip["departure_estimated"], "2026-05-01T10:02:00Z")
        self.assertEqual(trip["departure_delay"], 2)
        self.assertEqual(trip["arrival_planned"], "2026-05-01T10:23:00Z")
        self.assertEqual(trip["arrival_estimated"], "2026-05-01T10:25:00Z")
        self.assertEqual(trip["arrival_delay"], 2)
        # travel_time is arrival_estimated - departure_planned = 25 min.
        self.assertEqual(trip["travel_time"], 25)

    def test_response_dict_carries_only_v1_keys(self) -> None:
        with patch.object(
            v1, "fetch_trips", side_effect=lambda *a, **k: _canned_trips(k["limit"])
        ):
            trip = v1.find_trips("A", "B", limit=10, check_time=datetime(2026, 5, 1))[0]

        self.assertEqual(
            set(trip.keys()),
            {
                "from_id", "to_id", "from", "to",
                "departure_planned", "departure_estimated", "departure_delay",
                "arrival_planned", "arrival_estimated", "arrival_delay",
                "travel_time", "number",
            },
        )


class PartialPayloadTest(unittest.TestCase):
    """The v1 shaper must never crash on legs with missing timing info.

    The EFA endpoint may omit ``departureTimeEstimated`` etc. for legs
    in a planning-only state. Such legs must be filtered out rather
    than passed to the shaping functions (which would raise
    ``AttributeError`` / ``TypeError`` on ``None``).
    """

    _PAYLOAD_WITH_INCOMPLETE_LEG = {
        "journeys": [{
            "legs": [{
                "origin": {
                    "id": "de:08111:6118",
                    "name": "Stuttgart Hbf (tief)",
                    "departureTimePlanned": "2026-05-01T10:00:00Z",
                    # departureTimeEstimated missing -> estimated=None
                },
                "destination": {
                    "id": "de:08116:7800",
                    "name": "Esslingen",
                    "arrivalTimePlanned": "2026-05-01T10:23:00Z",
                    "arrivalTimeEstimated": "2026-05-01T10:25:00Z",
                },
                "transportation": {"number": "S1"},
            }],
        }],
    }

    def test_incomplete_leg_is_filtered_not_raised(self) -> None:
        with patch.object(
            v1,
            "fetch_trips",
            side_effect=lambda *a, **k: parse_response(
                self._PAYLOAD_WITH_INCOMPLETE_LEG, k["limit"]
            ),
        ):
            trips = v1.find_trips("A", "B", limit=10, check_time=datetime(2026, 5, 1))

        self.assertEqual(trips, [])


if __name__ == "__main__":
    unittest.main()
