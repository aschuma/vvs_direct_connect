
from os import getenv
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask.helpers import make_response
from waitress import serve
import service.v1 as v1
import service.v2 as v2


from_id = getenv("VVS_FROM", "5006333")
to_id = getenv("VVS_TO", "5007115")
limit = int(getenv("VVS_LIMIT", 10))
check_time_offset = int(getenv("VVS_TIME_OFFSET_MINUTES", 12))

print(f"\n\n")
print(f"----- VVS Direct Connect -----------------------------------")
print(f"Copyright (c) 2021-2024 aschuma (https://github.com/aschuma)")
print(f"------------------------------------------------------------")
print(f"\nSettings:")
print(f"\t- VVS_FROM={from_id}\n\t- VVS_TO={to_id}\n\t- VVS_LIMIT={limit}\n\t- VVS_TIME_OFFSET_MINUTES={check_time_offset}\n\n")


def check_time():
    return datetime.now() + timedelta(minutes=check_time_offset)


app = Flask(__name__)


@app.route('/api/v1/', methods=['GET'])
@app.route('/', methods=['GET'])
def get_trips_v1():
    try:
        return jsonify({'trips': v1.find_trips(from_id, to_id, limit, check_time=check_time()), 'status': 200})
    except Exception as e:
        return jsonify({'message': str(e), 'status': 500}), 500


@app.route('/api/v2/', methods=['GET'])
def get_trips_v2():
    try:
        return jsonify({'trips': v2.find_trips(from_id, to_id, limit, check_time=check_time()), 'status': 200})
    except Exception as e:
        return jsonify({'message': str(e), 'status': 500}), 500


@app.after_request
def after_request_func(data):
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=15151)
