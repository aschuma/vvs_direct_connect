"""Tests for :mod:`service.v2` (multi-leg lookup)."""

from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from service import v2
from service.vvs_client import parse_response


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "trip_response.json"


def _canned_trips(limit: int) -> list:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return parse_response(payload, limit)


class FindTripsTest(unittest.TestCase):
    def _find(self) -> list:
        with patch.object(
            v2, "fetch_trips", side_effect=lambda *a, **k: _canned_trips(k["limit"])
        ):
            return v2.find_trips("A", "B", limit=10, check_time=datetime(2026, 5, 1))

    def test_walk_only_trip_is_dropped(self) -> None:
        # Fixture has 3 journeys; one is walk-only and must not appear.
        trips = self._find()
        self.assertEqual(len(trips), 2)

    def test_walking_transfer_is_stripped_from_interchange_trip(self) -> None:
        interchange = self._find()[1]
        self.assertEqual(interchange["numbers"], ["S3", "S1"])
        self.assertEqual(interchange["number"], "S3,S1")
        self.assertEqual(len(interchange["details"]), 2)

    def test_aggregated_fields_use_first_and_last_leg(self) -> None:
        interchange = self._find()[1]
        # First leg origin is Bad Cannstatt at 11:00 planned / 11:00 estimated.
        self.assertEqual(interchange["from"], "Bad Cannstatt")
        self.assertEqual(interchange["departure_planned"], "2026-05-01T11:00:00Z")
        self.assertEqual(interchange["departure_delay"], 0)
        # Last leg destination is Hulb at 11:40 planned / 11:41 estimated.
        self.assertEqual(interchange["to"], "Hulb")
        self.assertEqual(interchange["arrival_planned"], "2026-05-01T11:40:00Z")
        self.assertEqual(interchange["arrival_estimated"], "2026-05-01T11:41:00Z")
        self.assertEqual(interchange["arrival_delay"], 1)
        # travel_time = 11:41 (est arr) - 11:00 (planned dep) = 41 min.
        self.assertEqual(interchange["travel_time"], 41)

    def test_details_show_per_leg_timestamps(self) -> None:
        interchange = self._find()[1]
        second_leg = interchange["details"][1]
        # After stripping the walking transfer this is the S1 leg.
        self.assertEqual(second_leg["number"], "S1")
        self.assertEqual(second_leg["from"], "Stuttgart Hbf (oben)")
        self.assertEqual(second_leg["to"], "Hulb")
        self.assertEqual(second_leg["departure_planned"], "2026-05-01T11:25:00Z")
        self.assertEqual(second_leg["arrival_estimated"], "2026-05-01T11:41:00Z")

    def test_direct_trip_is_still_returned_as_multi_leg_shape(self) -> None:
        direct = self._find()[0]
        self.assertEqual(direct["numbers"], ["S1"])
        self.assertEqual(direct["number"], "S1")
        self.assertEqual(len(direct["details"]), 1)


class PartialPayloadTest(unittest.TestCase):
    """The v2 shaper must never crash on legs with missing timing info.

    An interchange journey where one leg lacks timestamps must have
    that leg filtered out. If the resulting journey has no shapeable
    legs left it is dropped entirely, so the response always contains
    fully renderable trips.
    """

    _PAYLOAD_WITH_MIXED_LEGS = {
        "journeys": [{
            "legs": [
                {  # fully timed
                    "origin": {
                        "id": "A", "name": "A",
                        "departureTimePlanned": "2026-05-01T10:00:00Z",
                        "departureTimeEstimated": "2026-05-01T10:00:00Z",
                    },
                    "destination": {
                        "id": "B", "name": "B",
                        "arrivalTimePlanned": "2026-05-01T10:10:00Z",
                        "arrivalTimeEstimated": "2026-05-01T10:10:00Z",
                    },
                    "transportation": {"number": "S1"},
                },
                {  # arrivalTimeEstimated missing -> shaper would crash
                    "origin": {
                        "id": "B", "name": "B",
                        "departureTimePlanned": "2026-05-01T10:15:00Z",
                        "departureTimeEstimated": "2026-05-01T10:15:00Z",
                    },
                    "destination": {
                        "id": "C", "name": "C",
                        "arrivalTimePlanned": "2026-05-01T10:25:00Z",
                        # arrivalTimeEstimated missing on purpose
                    },
                    "transportation": {"number": "S2"},
                },
            ],
        }],
    }

    def test_incomplete_leg_is_dropped(self) -> None:
        with patch.object(
            v2,
            "fetch_trips",
            side_effect=lambda *a, **k: parse_response(
                self._PAYLOAD_WITH_MIXED_LEGS, k["limit"]
            ),
        ):
            trips = v2.find_trips("A", "B", limit=10, check_time=datetime(2026, 5, 1))

        # Only the fully timed leg survives; journey shape holds.
        self.assertEqual(len(trips), 1)
        self.assertEqual(trips[0]["numbers"], ["S1"])


if __name__ == "__main__":
    unittest.main()
