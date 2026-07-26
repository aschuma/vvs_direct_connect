"""Tests for the pure helpers in :mod:`service._shared`."""

from __future__ import annotations

import unittest
from datetime import datetime

from service._shared import (
    has_line_number,
    is_fully_timed,
    iso_ts,
    minutes_between,
    to_success_response,
)
from service.vvs_client import Leg, Stop


def _stop() -> Stop:
    """Return an empty stop for tests that only care about the leg's line."""
    return Stop(id=None, name=None, planned=None, estimated=None)


def _timed_stop() -> Stop:
    """Return a stop with both planned and estimated timestamps populated."""
    return Stop(
        id="X", name="X",
        planned=datetime(2026, 5, 1, 10, 0),
        estimated=datetime(2026, 5, 1, 10, 0),
    )


class IsoTsTest(unittest.TestCase):
    def test_formats_utc_with_trailing_z(self) -> None:
        self.assertEqual(
            iso_ts(datetime(2026, 5, 1, 10, 2, 3)),
            "2026-05-01T10:02:03Z",
        )


class MinutesBetweenTest(unittest.TestCase):
    def test_positive_delta(self) -> None:
        earlier = datetime(2026, 5, 1, 10, 0)
        later = datetime(2026, 5, 1, 10, 7)
        self.assertEqual(minutes_between(later, earlier), 7)

    def test_zero_delta(self) -> None:
        moment = datetime(2026, 5, 1, 10, 0)
        self.assertEqual(minutes_between(moment, moment), 0)

    def test_negative_delta_truncates_toward_zero(self) -> None:
        # earlier > later -> negative seconds; int() truncates toward zero
        earlier = datetime(2026, 5, 1, 10, 5)
        later = datetime(2026, 5, 1, 10, 0)
        self.assertEqual(minutes_between(later, earlier), -5)


class HasLineNumberTest(unittest.TestCase):
    def test_true_for_transport_leg(self) -> None:
        self.assertTrue(has_line_number(Leg(_stop(), _stop(), "S1")))

    def test_false_for_walking_transfer(self) -> None:
        self.assertFalse(has_line_number(Leg(_stop(), _stop(), None)))


class IsFullyTimedTest(unittest.TestCase):
    def test_true_when_all_four_timestamps_present(self) -> None:
        leg = Leg(_timed_stop(), _timed_stop(), "S1")
        self.assertTrue(is_fully_timed(leg))

    def test_false_when_origin_planned_missing(self) -> None:
        broken = Stop(id="X", name="X", planned=None, estimated=_timed_stop().estimated)
        self.assertFalse(is_fully_timed(Leg(broken, _timed_stop(), "S1")))

    def test_false_when_destination_estimated_missing(self) -> None:
        broken = Stop(id="Y", name="Y", planned=_timed_stop().planned, estimated=None)
        self.assertFalse(is_fully_timed(Leg(_timed_stop(), broken, "S1")))

    def test_false_when_all_timestamps_missing(self) -> None:
        self.assertFalse(is_fully_timed(Leg(_stop(), _stop(), "S1")))


class ToSuccessResponseTest(unittest.TestCase):
    def test_wraps_trips_and_sets_status_200(self) -> None:
        trips = [{"number": "S1"}]
        self.assertEqual(
            to_success_response(trips),
            {"trips": trips, "status": 200},
        )

    def test_empty_trip_list_is_preserved(self) -> None:
        self.assertEqual(to_success_response([]), {"trips": [], "status": 200})


if __name__ == "__main__":
    unittest.main()
