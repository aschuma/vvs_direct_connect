
from os import getenv
from datetime import datetime, timedelta
from vvspy.trip import get_trips


def iso_ts(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')


def extract_data(connections):
    connection = connections[0]
    last_connection = connections[len(connections) - 1]
    departure_planed = connection.origin.departure_time_planned
    departure_estimated = connection.origin.departure_time_estimated
    departure_delta = int(
        (departure_estimated - departure_planed).total_seconds() / 60)
    arrival_planed = last_connection.destination.arrival_time_planned
    arrival_estimated = last_connection.destination.arrival_time_estimated
    arrival_delta = int(
        (arrival_estimated - arrival_planed).total_seconds() / 60)

    travel_time = int(
        (arrival_estimated - departure_planed).total_seconds() / 60)

    number_list = [c.transportation.number for c in connections]
    number = ",".join(number_list)

    return {
        "from_id": connection.origin.id,
        "to_id": connection.destination.id,
        "from": last_connection.origin.name,
        "to": last_connection.destination.name,
        "departure_planned": iso_ts(departure_planed),
        "departure_estimated": iso_ts(departure_estimated),
        "departure_delay": departure_delta,
        "arrival_planed": iso_ts(arrival_planed),
        "arrival_estimated": iso_ts(arrival_estimated),
        "arrival_delay": arrival_delta,
        "travel_time": travel_time,
        "number": number,
        "numbers": number_list,
        "details": [{
            "from": c.origin.name,
            "from_id": c.origin.id,
            "to": c.destination.name,
            "to_id": c.destination.id,
            "number": c.transportation.number,
            "departure_planed": iso_ts(connection.origin.departure_time_planned),
            "departure_estimated": iso_ts(connection.origin.departure_time_estimated),
            "arrival_planed": iso_ts(connection.destination.arrival_time_planned),
            "arrival_estimated": iso_ts(connection.destination.arrival_time_estimated)
        } for c in connections]
    }


def find_trips(from_id, to_id, limit, check_time):
    trips = get_trips(from_id, to_id, limit=limit, check_time=check_time)
    connections_list = [
        [connection for connection in trip.connections if connection.transportation.number is not None] for trip in trips]

    trip_data_list = [extract_data(connections)
                      for connections in connections_list if len(connections) > 0]
    return trip_data_list
