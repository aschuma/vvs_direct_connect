"""Tests for the HTTP layer in :mod:`app`.

These tests use Flask's test client (no live server, no waitress) to
exercise the routing, error handling and content-type behaviour of
the application.
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

import app as app_module
import service.v1 as v1
import service.v2 as v2


class HealthTest(unittest.TestCase):
    def test_health_returns_200_json(self) -> None:
        with app_module.app.test_client() as client:
            response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.get_json(), {"status": 200})


class HttpErrorTest(unittest.TestCase):
    """404, 405 etc. must be JSON, not HTML."""

    def test_404_returns_json_envelope(self) -> None:
        with app_module.app.test_client() as client:
            response = client.get("/does/not/exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        body = response.get_json()
        self.assertEqual(body["status"], 404)
        self.assertIn("message", body)

    def test_405_returns_json_envelope(self) -> None:
        with app_module.app.test_client() as client:
            response = client.post("/api/v1/")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        body = response.get_json()
        self.assertEqual(body["status"], 405)
        self.assertIn("message", body)

    def test_404_body_is_valid_json(self) -> None:
        """Regression guard: the previous after_request hook mislabeled
        HTML error pages as ``application/json`` -- ``json.loads`` on
        the body would then raise. This test would have caught it."""
        with app_module.app.test_client() as client:
            response = client.get("/nope")
        # Must not raise:
        json.loads(response.get_data(as_text=True))


class TripEndpointTest(unittest.TestCase):
    """Successful trip endpoints must serve JSON with the correct envelope."""

    _FAKE_V1_ENVELOPE = {"trips": [{"number": "S1"}], "status": 200}
    _FAKE_V2_ENVELOPE = {"trips": [{"numbers": ["S1"]}], "status": 200}

    def test_get_v1_serves_service_envelope(self) -> None:
        with patch.object(v1, "find_trips", return_value=self._FAKE_V1_ENVELOPE):
            with app_module.app.test_client() as client:
                response = client.get("/api/v1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.get_json(), self._FAKE_V1_ENVELOPE)

    def test_root_route_aliases_v1(self) -> None:
        with patch.object(v1, "find_trips", return_value=self._FAKE_V1_ENVELOPE):
            with app_module.app.test_client() as client:
                response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), self._FAKE_V1_ENVELOPE)

    def test_get_v2_serves_service_envelope(self) -> None:
        with patch.object(v2, "find_trips", return_value=self._FAKE_V2_ENVELOPE):
            with app_module.app.test_client() as client:
                response = client.get("/api/v2/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.get_json(), self._FAKE_V2_ENVELOPE)

    def test_service_exception_becomes_500_envelope(self) -> None:
        with patch.object(v1, "find_trips", side_effect=RuntimeError("boom")):
            with app_module.app.test_client() as client:
                response = client.get("/api/v1/")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        body = response.get_json()
        self.assertEqual(body["status"], 500)
        self.assertIn("boom", body["message"])


if __name__ == "__main__":
    unittest.main()
