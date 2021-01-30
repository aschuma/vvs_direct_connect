
from os import getenv
from datetime import datetime, timedelta
from flask import Flask, Response, jsonify
from flask.helpers import make_response
from vvspy.trip import get_trips


from_id = int(getenv("VVS_FROM", 5006333))
to_id = int(getenv("VVS_TO", 5007115))
limit = int(getenv("VVS_LIMIT", 10))
check_time_offset = int(getenv("VVS_TIME_OFFSET_MINUTES", 12))
flask_debug = bool(getenv("VVS_FLASK_DEBUG", False))


def check_time():
    return datetime.now() + timedelta(minutes=check_time_offset)


def iso_ts(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')


def extract_data(connection):
    planed = connection.origin.departure_time_planned
    estimated = connection.origin.departure_time_estimated
    delta = int((estimated - planed).total_seconds() / 60)
    return {
        "from_id": from_id,
        "to_id": to_id,
        "from": connection.origin.name,
        "to": connection.destination.name,
        "planned": iso_ts(planed),
        "estimated": iso_ts(estimated),
        "delay": delta
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


if __name__ == '__main__':
    app.run(debug=flask_debug)
