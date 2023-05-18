[![CodeQL](https://github.com/aschuma/vvs_direct_connect/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/aschuma/vvs_direct_connect/actions/workflows/codeql-analysis.yml)


# VVS Direct Connect REST Service
Simple REST service providing connection data for a dedicated VVS connection. VVS is the local public transport in Stuttgart. Only direct connections are supported.

## Start Server
```shell
$ docker run --rm -p5000:5000 -ti \
   -e VVS_FROM=de:08111:6118 \
   -e VVS_TO=de:08116:7800 \
   aschuma/vvs_direct_connect:latest

----- VVS Direct Connect -----------------------------------
Copyright (c) 2021-2023 aschuma (https://github.com/aschuma)
------------------------------------------------------------

Settings:
	- VVS_FROM=de:08111:6118
	- VVS_TO=de:08116:7800
	- VVS_LIMIT=10
	- VVS_TIME_OFFSET_MINUTES=12

```

Supported platforms:

* linux/amd64
* linux/arm64
* linux/arm/v7 (PI 4B)

## Call Rest Endpoint
```shell
$ curl 127.0.0.1:5000

{
  "status": 200,
  "trips": [
    {
      "arrival_delay": 0,
      "arrival_estimated": "2023-05-18T21:02:00Z",
      "arrival_planed": "2023-05-18T21:02:00Z",
      "departure_delay": 0,
      "departure_estimated": "2023-05-18T20:52:00Z",
      "departure_planned": "2023-05-18T20:52:00Z",
      "from": "Stuttgart Hauptbahnhof (oben)",
      "from_id": "de:08111:6118",
      "number": "MEX12",
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800",
      "travel_time": 10
    },
    {
      "arrival_delay": 2,
      "arrival_estimated": "2023-05-18T21:16:00Z",
      "arrival_planed": "2023-05-18T21:14:00Z",
      "departure_delay": 0,
      "departure_estimated": "2023-05-18T21:03:00Z",
      "departure_planned": "2023-05-18T21:03:00Z",
      "from": "Stuttgart Hauptbahnhof (oben)",
      "from_id": "de:08111:6118",
      "number": "MEX16",
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800",
      "travel_time": 13
    },
    {
      "arrival_delay": 0,
      "arrival_estimated": "2023-05-18T21:34:00Z",
      "arrival_planed": "2023-05-18T21:34:00Z",
      "departure_delay": 0,
      "departure_estimated": "2023-05-18T21:23:00Z",
      "departure_planned": "2023-05-18T21:23:00Z",
      "from": "Stuttgart Hauptbahnhof (oben)",
      "from_id": "de:08111:6118",
      "number": "MEX18",
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800",
      "travel_time": 11
    },
    {
      "arrival_delay": 0,
      "arrival_estimated": "2023-05-18T21:42:00Z",
      "arrival_planed": "2023-05-18T21:42:00Z",
      "departure_delay": 1,
      "departure_estimated": "2023-05-18T21:26:00Z",
      "departure_planned": "2023-05-18T21:25:00Z",
      "from": "Stuttgart Hauptbahnhof (tief)",
      "from_id": "de:08111:6118",
      "number": "S1",
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800",
      "travel_time": 17
    }
  ]
}

```
## Parameter

- `VVS_FROM` departure station id 
- `VVS_TO` destination station id 
- `VVS_LIMIT` max number of trips to fetch
- `VVS_TIME_OFFSET_MINUTES` walking distance to departure station

## Obtaining the Station IDs

Please consult [https://www.openvvs.de/dataset/haltestellen](https://www.openvvs.de/dataset/haltestellen) to identify the origin and destination stations. 

Alternatively, you can use the online timetable information to get the IDs. To do so, open VVS [https://www3.vvs.de/](https://www3.vvs.de/) in your browser. Enter origin and destination stations and click submit, e.g. `origin=Stuttgart` and `destination=Esslingen`:

![VVS](https://raw.githubusercontent.com/aschuma/vvs_direct_connect/main/doc/010_search.png)

Copy the Browser URL into a text editor:

![Search](https://raw.githubusercontent.com/aschuma/vvs_direct_connect/main/doc/020_url.png)

Search for the `orig`and `dest`parameters and the associated values. In this case `de:08111:6118` is the ID of the origin station (Stuttgart).  The ID of the destination station (Esslingen) is `de:08116:7800`.

![URL](https://raw.githubusercontent.com/aschuma/vvs_direct_connect/main/doc/030_url_parameter.png)

## Credits
Credits to [Yannick](https://github.com/zaanposni) for [vvspy](https://pypi.org/project/vvspy/)

## Further Information
* [https://www.openvvs.de/](https://www.openvvs.de/)
* [https://www.openvvs.de/dataset/haltestellen](https://www.openvvs.de/dataset/haltestellen)
* [https://www.vdv.de/ip-kom-oev.aspx](https://www.vdv.de/ip-kom-oev.aspx)
* [https://github.com/VDVde/TRIAS](https://github.com/VDVde/TRIAS)
