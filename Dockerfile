FROM python:3.13-slim-bookworm AS builder

WORKDIR /usr/src/app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


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

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean autoclean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/* \
    && useradd --system --create-home --shell /usr/sbin/nologin appuser

COPY --from=builder /opt/venv /opt/venv

COPY . .

USER appuser

EXPOSE 15151

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:15151/health', timeout=4).status == 200 else 1)"]

CMD [ "python", "./app.py" ]


