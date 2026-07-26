"""Tests for :mod:`service.vvs_client` (parser + URL builder)."""

from __future__ import annotations

import json
import unittest
from datetime import datetime
from enum import Enum
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from service.vvs_client import (
    API_URL,
    Trip,
    _build_url,
    _station_value,
    parse_response,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "trip_response.json"


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


class ParseResponseTest(unittest.TestCase):
    def test_returns_all_trips_when_limit_is_high(self) -> None:
        trips = parse_response(_load_fixture(), limit=10)
        self.assertEqual(len(trips), 3)
        self.assertTrue(all(isinstance(t, Trip) for t in trips))

    def test_limit_truncates_the_result(self) -> None:
        trips = parse_response(_load_fixture(), limit=2)
        self.assertEqual(len(trips), 2)

    def test_none_payload_yields_empty_list(self) -> None:
        self.assertEqual(parse_response(None, limit=5), [])

    def test_direct_trip_is_parsed_correctly(self) -> None:
        trip = parse_response(_load_fixture(), limit=10)[0]
        self.assertEqual(len(trip.legs), 1)
        leg = trip.legs[0]
        self.assertEqual(leg.line_number, "S1")
        self.assertEqual(leg.origin.id, "de:08111:6118")
        self.assertEqual(leg.origin.name, "Stuttgart Hbf (tief)")
        self.assertEqual(leg.origin.planned, datetime(2026, 5, 1, 10, 0))
        self.assertEqual(leg.origin.estimated, datetime(2026, 5, 1, 10, 2))
        self.assertEqual(leg.destination.id, "de:08116:7800")
        self.assertEqual(leg.destination.estimated, datetime(2026, 5, 1, 10, 25))

    def test_interchange_trip_keeps_walking_leg(self) -> None:
        # ``parse_response`` should not filter walking legs; that's the
        # responsibility of the v2 service.
        interchange = parse_response(_load_fixture(), limit=10)[1]
        self.assertEqual(len(interchange.legs), 3)
        line_numbers = [leg.line_number for leg in interchange.legs]
        self.assertEqual(line_numbers, ["S3", None, "S1"])

    def test_missing_timestamps_become_none(self) -> None:
        payload = {"journeys": [{"legs": [{
            "origin": {"id": "a", "name": "A"},
            "destination": {"id": "b", "name": "B"},
            "transportation": {"number": "X"},
        }]}]}
        leg = parse_response(payload, limit=1)[0].legs[0]
        self.assertIsNone(leg.origin.planned)
        self.assertIsNone(leg.destination.estimated)


class StationValueTest(unittest.TestCase):
    class _Station(Enum):
        HBF = "de:08111:6118"

    def test_string_passes_through(self) -> None:
        self.assertEqual(_station_value("de:08111:6118"), "de:08111:6118")

    def test_int_is_stringified(self) -> None:
        self.assertEqual(_station_value(5006333), "5006333")

    def test_enum_uses_value(self) -> None:
        self.assertEqual(_station_value(self._Station.HBF), "de:08111:6118")


class BuildUrlTest(unittest.TestCase):
    def test_url_carries_caller_specific_params(self) -> None:
        url = _build_url("A", "B", datetime(2026, 5, 1, 10, 7))
        self.assertTrue(url.startswith(API_URL + "?"))

        params = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        self.assertEqual(params["name_origin"], "A")
        self.assertEqual(params["name_destination"], "B")
        self.assertEqual(params["itdDate"], "20260501")
        self.assertEqual(params["itdTime"], "1007")
        # Sanity-check a baseline param is preserved.
        self.assertEqual(params["outputFormat"], "rapidJSON")


if __name__ == "__main__":
    unittest.main()
