FROM python:3.11-slim-bullseye

WORKDIR /usr/src/app

ENV VVS_FROM="de:08116:2103" \
    VVS_TO="de:08111:6118" \
    VVS_LIMIT="10" \
    VVS_TIME_OFFSET_MINUTES="12" \
    VVS_FLASK_DEBUG="False" \
    TZ="Europe/Berlin"

COPY requirements.txt .

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean autoclean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 15151

CMD [ "python", "./app.py" ]


