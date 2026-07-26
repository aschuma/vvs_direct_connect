# syntax=docker/dockerfile:1.7
#
# Two-stage build:
#   1. builder -- uses the official uv image (which already ships uv and
#      the pinned CPython) to resolve and install runtime dependencies
#      into an isolated virtualenv.
#   2. runtime  -- a slim CPython image that receives only the venv and
#      the application source. uv itself is not needed at runtime.

# --------------------------------------------------------------------------- #
# Builder
# --------------------------------------------------------------------------- #
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /usr/src/app

# Use a project-local venv path that we can copy verbatim into the
# runtime stage. UV_LINK_MODE=copy avoids hardlink warnings when the
# uv cache lives on a different filesystem (i.e. a BuildKit cache mount).
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# First layer: dependencies only. Invalidated when either the
# lockfile or the pyproject changes; unaffected by source-code edits.
COPY pyproject.toml uv.lock .python-version ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Second layer: application source. Cheap to invalidate.
COPY . .


# --------------------------------------------------------------------------- #
# Runtime
# --------------------------------------------------------------------------- #
FROM python:3.13-slim-bookworm

WORKDIR /usr/src/app

ENV VVS_FROM="de:08116:2103" \
    VVS_TO="de:08111:6118" \
    VVS_LIMIT="10" \
    VVS_TIME_OFFSET_MINUTES="12" \
    VVS_FLASK_DEBUG="False" \
    TZ="Europe/Berlin" \
    PYTHONUNBUFFERED="1" \
    PYTHONDONTWRITEBYTECODE="1" \
    PATH="/opt/venv/bin:$PATH"

RUN useradd --system --create-home --shell /usr/sbin/nologin appuser

# Bring in the pre-populated virtualenv and the application source.
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/src/app /usr/src/app

USER appuser

EXPOSE 15151

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:15151/health', timeout=4).status == 200 else 1)"]

CMD ["python", "./app.py"]
