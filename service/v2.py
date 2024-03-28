
from os import getenv
from datetime import datetime, timedelta
from vvspy.trip import get_trips


def iso_ts(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')


def extract_data(connection):
    departure_planed = connection.origin.departure_time_planned
    departure_estimated = connection.origin.departure_time_estimated
    departure_delta = int(
        (departure_estimated - departure_planed).total_seconds() / 60)
    arrival_planed = connection.destination.arrival_time_planned
    arrival_estimated = connection.destination.arrival_time_estimated
    arrival_delta = int(
        (arrival_estimated - arrival_planed).total_seconds() / 60)

    travel_time = int(
        (arrival_estimated - departure_planed).total_seconds() / 60)

    return {
        "from_id": connection.origin.id,
        "to_id": connection.destination.id,
        "from": connection.origin.name,
        "to": connection.destination.name,
        "departure_planned": iso_ts(departure_planed),
        "departure_estimated": iso_ts(departure_estimated),
        "departure_delay": departure_delta,
        "arrival_planed": iso_ts(arrival_planed),
        "arrival_estimated": iso_ts(arrival_estimated),
        "arrival_delay": arrival_delta,
        "travel_time": travel_time,
        "number": connection.transportation.number
    }


def find_trips(from_id, to_id, limit, check_time):
    trips = get_trips(from_id, to_id, limit=limit, check_time=check_time)
    trip_data_list = [extract_data(trip.connections[0])
                      for trip in trips if len(trip.connections) == 1]
    return trip_data_list
