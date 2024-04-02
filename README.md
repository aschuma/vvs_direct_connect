[![CodeQL](https://github.com/aschuma/vvs_direct_connect/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/aschuma/vvs_direct_connect/actions/workflows/codeql-analysis.yml)


# VVS Direct Connect REST Service
Simple REST service providing connection data for a dedicated VVS connection. VVS is the local public transport in Stuttgart. 

The REST endpoints `/api/v1/` and `/` (this is an alias for `/api/v1/`) exclusively handle direct connections. Additionally, the `/api/v2/` endpoint supports interchange stations.

## Start Server
```shell
$ docker run --rm -p15151:15151 -ti \
   -e VVS_FROM=de:08111:6118 \
   -e VVS_TO=de:08116:7800 \
   aschuma/vvs_direct_connect:latest

----- VVS Direct Connect -----------------------------------
Copyright (c) 2021-2024 aschuma (https://github.com/aschuma)
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

⚠️ Kindly note that the default port has been updated to 15151.

```shell
$ curl 127.0.0.1:15151/api/v2/

{
  "status": 200,
  "trips": [
    {
      "arrival_delay": 0,
      "arrival_estimated": "2024-04-02T09:14:00Z",
      "arrival_planed": "2024-04-02T09:14:00Z",
      "departure_delay": 0,
      "departure_estimated": "2024-04-02T09:03:00Z",
      "departure_planned": "2024-04-02T09:03:00Z",
      "details": [
        {
          "arrival_estimated": "2024-04-02T09:14:00Z",
          "arrival_planed": "2024-04-02T09:14:00Z",
          "departure_estimated": "2024-04-02T09:03:00Z",
          "departure_planed": "2024-04-02T09:03:00Z",
          "from": "Stuttgart Hauptbahnhof (oben)",
          "from_id": "de:08111:6115:6:12",
          "number": "MEX16",
          "to": "Esslingen (N)",
          "to_id": "de:08116:7800:2:5"
        }
      ],
      "from": "Stuttgart Hauptbahnhof (oben)",
      "from_id": "de:08111:6115:6:12",
      "number": "MEX16",
      "numbers": [
        "MEX16"
      ],
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800:2:5",
      "travel_time": 11
    },
    {
      "arrival_delay": 0,
      "arrival_estimated": "2024-04-02T09:27:00Z",
      "arrival_planed": "2024-04-02T09:27:00Z",
      "departure_delay": 1,
      "departure_estimated": "2024-04-02T09:11:00Z",
      "departure_planned": "2024-04-02T09:10:00Z",
      "details": [
        {
          "arrival_estimated": "2024-04-02T09:27:00Z",
          "arrival_planed": "2024-04-02T09:27:00Z",
          "departure_estimated": "2024-04-02T09:11:00Z",
          "departure_planed": "2024-04-02T09:10:00Z",
          "from": "Stuttgart Hauptbahnhof (tief)",
          "from_id": "de:08111:6118:1:102",
          "number": "S1",
          "to": "Esslingen (N)",
          "to_id": "de:08116:7800:1:8"
        }
      ],
      "from": "Stuttgart Hauptbahnhof (tief)",
      "from_id": "de:08111:6118:1:102",
      "number": "S1",
      "numbers": [
        "S1"
      ],
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800:1:8",
      "travel_time": 17
    },
    {
      "arrival_delay": 0,
      "arrival_estimated": "2024-04-02T09:42:00Z",
      "arrival_planed": "2024-04-02T09:42:00Z",
      "departure_delay": 1,
      "departure_estimated": "2024-04-02T09:26:00Z",
      "departure_planned": "2024-04-02T09:25:00Z",
      "details": [
        {
          "arrival_estimated": "2024-04-02T09:42:00Z",
          "arrival_planed": "2024-04-02T09:42:00Z",
          "departure_estimated": "2024-04-02T09:26:00Z",
          "departure_planed": "2024-04-02T09:25:00Z",
          "from": "Stuttgart Hauptbahnhof (tief)",
          "from_id": "de:08111:6118:1:102",
          "number": "S1",
          "to": "Esslingen (N)",
          "to_id": "de:08116:7800:1:8"
        }
      ],
      "from": "Stuttgart Hauptbahnhof (tief)",
      "from_id": "de:08111:6118:1:102",
      "number": "S1",
      "numbers": [
        "S1"
      ],
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800:1:8",
      "travel_time": 17
    },
    {
      "arrival_delay": 0,
      "arrival_estimated": "2024-04-02T09:48:00Z",
      "arrival_planed": "2024-04-02T09:48:00Z",
      "departure_delay": 0,
      "departure_estimated": "2024-04-02T09:39:00Z",
      "departure_planned": "2024-04-02T09:39:00Z",
      "details": [
        {
          "arrival_estimated": "2024-04-02T09:48:00Z",
          "arrival_planed": "2024-04-02T09:48:00Z",
          "departure_estimated": "2024-04-02T09:39:00Z",
          "departure_planed": "2024-04-02T09:39:00Z",
          "from": "Stuttgart Hauptbahnhof (oben)",
          "from_id": "de:08111:6115:8:15",
          "number": "RE5",
          "to": "Esslingen (N)",
          "to_id": "de:08116:7800:2:5"
        }
      ],
      "from": "Stuttgart Hauptbahnhof (oben)",
      "from_id": "de:08111:6115:8:15",
      "number": "RE5",
      "numbers": [
        "RE5"
      ],
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800:2:5",
      "travel_time": 9
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

## Address Support - Obtaining the Street IDs

The REST endpoint `/api/v2` additionally provides also some support for addresses within the VVS area. The format for the address _Konrad Adenauer Str 32_ (Staatsgalerie) is as follows: `streetID:1500001775:32:8111000:51:Konrad-Adenauer-Straße:Stuttgart:Konrad-Adenauer-Straße::Konrad-Adenauer-Straße:70173:ANY:DIVA_SINGLEHOUSE:3513826:755185:NBWT:VVS:0`.

You can also obtain the corresponding value through a VVS query as described above.

## Credits
Credits to [Yannick](https://github.com/zaanposni) for [vvspy](https://pypi.org/project/vvspy/)

## Further Information
* [https://www.openvvs.de/](https://www.openvvs.de/)
* [https://www.openvvs.de/dataset/haltestellen](https://www.openvvs.de/dataset/haltestellen)
* [https://www.vdv.de/ip-kom-oev.aspx](https://www.vdv.de/ip-kom-oev.aspx)
* [https://github.com/VDVde/TRIAS](https://github.com/VDVde/TRIAS)
