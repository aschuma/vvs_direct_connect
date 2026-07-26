"""HTTP entry point for the VVS Direct Connect service.

This module wires the two trip-lookup services (:mod:`service.v1` for
direct connections and :mod:`service.v2` for multi-leg journeys) to a
small Flask application and serves it through the production-grade
waitress WSGI server.

Endpoints
---------
* ``GET /``         -- alias of ``/api/v1/``.
* ``GET /api/v1/``  -- direct connections only, JSON response.
* ``GET /api/v2/``  -- multi-leg (interchange) connections, JSON response.
* ``GET /health``   -- liveness probe used by container orchestrators.

Configuration
-------------
All settings are read from environment variables at import time:

===========================  ===============================================
``VVS_FROM``                 Departure station id (default ``"5006333"``).
``VVS_TO``                   Arrival station id (default ``"5007115"``).
``VVS_LIMIT``                Upper bound for trips per request
                             (default ``10``).
``VVS_TIME_OFFSET_MINUTES``  Minutes added to ``now`` when planning trips
                             (default ``12``). Useful to skip departures
                             the user could no longer reach on foot.
===========================  ===============================================
"""

from __future__ import annotations

from datetime import datetime, timedelta
from os import getenv
from typing import Any

from flask import Flask, Response, jsonify
from waitress import serve

import service.v1 as v1
import service.v2 as v2

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
# Values are captured once at import time; the process is expected to
# be restarted (e.g. via the container orchestrator) when they change.
FROM_ID: str = getenv("VVS_FROM", "5006333")
TO_ID: str = getenv("VVS_TO", "5007115")
LIMIT: int = int(getenv("VVS_LIMIT", "10"))
CHECK_TIME_OFFSET_MINUTES: int = int(getenv("VVS_TIME_OFFSET_MINUTES", "12"))

HTTP_HOST: str = "0.0.0.0"
HTTP_PORT: int = 15151


def _print_banner() -> None:
    """Print a human-readable startup banner listing the active settings.

    Deliberately uses ``print`` so the banner shows up on stdout even
    when logging has not yet been configured.
    """
    print(
        f"\n\n----- VVS Direct Connect -----------------------------------\n"
        f"Copyright (c) 2021-2024 aschuma (https://github.com/aschuma)\n"
        f"------------------------------------------------------------\n\nSettings:\n"
        f"\t- VVS_FROM={FROM_ID}\n\t- VVS_TO={TO_ID}\n"
        f"\t- VVS_LIMIT={LIMIT}\n\t- VVS_TIME_OFFSET_MINUTES={CHECK_TIME_OFFSET_MINUTES}\n\n"
    )


_print_banner()


def _check_time() -> datetime:
    """Return the point in time to plan trips for.

    The current wall-clock time is shifted into the future by
    :data:`CHECK_TIME_OFFSET_MINUTES` so that the returned connections
    are actually reachable by the user.
    """
    return datetime.now() + timedelta(minutes=CHECK_TIME_OFFSET_MINUTES)


# --------------------------------------------------------------------------- #
# Flask application
# --------------------------------------------------------------------------- #
app = Flask(__name__)


def _error_response(exc: Exception) -> tuple[Response, int]:
    """Wrap an unexpected exception in the standard error envelope.

    The error envelope stays in the HTTP layer because it is tied to
    exception handling and HTTP status codes, which are not service
    concerns. The mirror success envelope is produced by the service
    modules themselves.
    """
    return jsonify({"message": str(exc), "status": 500}), 500


def _get_trips(service_func: Any) -> Response | tuple[Response, int]:
    """Call ``service_func`` with the configured station ids and return JSON."""
    try:
        return jsonify(service_func(FROM_ID, TO_ID, LIMIT, check_time=_check_time()))
    except Exception as exc:
        return _error_response(exc)


@app.route("/api/v1/", methods=["GET"])
@app.route("/", methods=["GET"])
def get_trips_v1() -> Response | tuple[Response, int]:
    """Return direct connections (single-leg trips) as JSON."""
    return _get_trips(v1.find_trips)


@app.route("/api/v2/", methods=["GET"])
def get_trips_v2() -> Response | tuple[Response, int]:
    """Return multi-leg (interchange) trips as JSON."""
    return _get_trips(v2.find_trips)


@app.route("/health", methods=["GET"])
def health() -> Response:
    """Liveness probe. Always returns HTTP 200 with a minimal JSON body."""
    return jsonify({"status": 200})


@app.after_request
def _force_json_content_type(response: Response) -> Response:
    """Ensure every response advertises ``application/json``.

    Flask's :func:`jsonify` already sets this header, but the hook
    guarantees the behaviour even for custom responses added in the
    future.
    """
    response.headers["Content-Type"] = "application/json"
    return response


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    serve(app, host=HTTP_HOST, port=HTTP_PORT)
