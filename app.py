
from os import getenv
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask.helpers import make_response
from waitress import serve
from vvspy.trip import get_trips


from_id = getenv("VVS_FROM", "5006333")
to_id = getenv("VVS_TO", "5007115")
limit = int(getenv("VVS_LIMIT", 10))
check_time_offset = int(getenv("VVS_TIME_OFFSET_MINUTES", 12))

print(f"\n\n")
print(f"----- VVS Direct Connect ------------------------------")
print(f"Copyright (c) 2021-2023 aschuma (https://github.com/aschuma)")
print(f"-------------------------------------------------------")
print(f"\nSettings:")
print(f"\t- VVS_FROM={from_id}\n\t- VVS_TO={to_id}\n\t- VVS_LIMIT={limit}\n\t- VVS_TIME_OFFSET_MINUTES={check_time_offset}\n\n")


def check_time():
    return datetime.now() + timedelta(minutes=check_time_offset)


def iso_ts(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')


def extract_data(connection):
    departure_planed = connection.origin.departure_time_planned
    departure_estimated = connection.origin.departure_time_estimated
    departure_delta = int((departure_estimated - departure_planed).total_seconds() / 60)
    arrival_planed = connection.destination.arrival_time_planned
    arrival_estimated = connection.destination.arrival_time_estimated
    arrival_delta = int((arrival_estimated - arrival_planed).total_seconds() / 60)
    return {
        "from_id": from_id,
        "to_id": to_id,
        "from": connection.origin.name,
        "to": connection.destination.name,
        "departure_planned": iso_ts(departure_planed),
        "departure_estimated": iso_ts(departure_estimated),
        "departure_delay": departure_delta,
        "arrival_planed": iso_ts(arrival_planed),
        "arrival_estimated": iso_ts(arrival_estimated),
        "arrival_delay": arrival_delta,
        "number": connection.transportation.number
    }


def find_trips():
    trips = get_trips(from_id, to_id, limit=limit, check_time=check_time())
    trip_data_list = [extract_data(trip.connections[0])
                      for trip in trips if len(trip.connections) == 1]
    return trip_data_list


app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_tasks():
    try:
        return jsonify({'trips': find_trips(), 'status': 200})
    except Exception as e:
        return jsonify({'message': str(e), 'status': 500}), 500


@app.after_request
def after_request_func(data):
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5001)
