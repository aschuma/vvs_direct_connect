# VVS Direct Connect REST Service
Simple REST service providing connection data for a dedicated VVS connection. VVS is the local public transport in Stuttgart. Only direct connections are supported.

## Start Server

```shell
$ docker run --rm -p5000:5000 -ti \
   -e VVS_FROM=de:08111:6118 \
   -e VVS_TO=de:08116:7800 \
   aschuma/vvs_direct_connect:latest

----- VVS Direct Connect ------------------------------
Copyright (c) 2021 aschuma (https://github.com/aschuma)
-------------------------------------------------------

Settings:
	- VVS_FROM=de:08111:6118
	- VVS_TO=de:08116:7800
	- VVS_LIMIT=10
	- VVS_TIME_OFFSET_MINUTES=12


Serving on http://0.0.0.0:5000
```
## Call Rest Endpoint
```shell
$ curl 127.0.0.1:5000

{
  "status": 200,
  "trips": [
    {
      "arrival_delay": 0,
      "arrival_estimated": "2021-01-31T11:11:00Z",
      "arrival_planed": "2021-01-31T11:11:00Z",
      "departure_delay": 0,
      "departure_estimated": "2021-01-31T11:01:00Z",
      "departure_planned": "2021-01-31T11:01:00Z",
      "from": "Stuttgart Hauptbahnhof (oben)",
      "from_id": "de:08111:6118",
      "number": "RE5",
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800"
    },
    {
      "arrival_delay": 0,
      "arrival_estimated": "2021-01-31T11:34:00Z",
      "arrival_planed": "2021-01-31T11:34:00Z",
      "departure_delay": 0,
      "departure_estimated": "2021-01-31T11:23:00Z",
      "departure_planned": "2021-01-31T11:23:00Z",
      "from": "Stuttgart Hauptbahnhof (oben)",
      "from_id": "de:08111:6118",
      "number": "RB18",
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800"
    },
    {
      "arrival_delay": 0,
      "arrival_estimated": "2021-01-31T11:40:00Z",
      "arrival_planed": "2021-01-31T11:40:00Z",
      "departure_delay": 0,
      "departure_estimated": "2021-01-31T11:29:00Z",
      "departure_planned": "2021-01-31T11:29:00Z",
      "from": "Stuttgart Hauptbahnhof (oben)",
      "from_id": "de:08111:6118",
      "number": "RB16",
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800"
    },
    {
      "arrival_delay": 0,
      "arrival_estimated": "2021-01-31T11:49:00Z",
      "arrival_planed": "2021-01-31T11:49:00Z",
      "departure_delay": 0,
      "departure_estimated": "2021-01-31T11:40:00Z",
      "departure_planned": "2021-01-31T11:40:00Z",
      "from": "Stuttgart Hauptbahnhof (oben)",
      "from_id": "de:08111:6118",
      "number": "RE5",
      "to": "Esslingen (N)",
      "to_id": "de:08116:7800"
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
