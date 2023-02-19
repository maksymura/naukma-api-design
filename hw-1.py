import datetime as dt
import json
import os

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "api_token"

app = Flask(__name__)


def get_weather(location, date):
    url_base_url = f"http://api.weatherapi.com/v1/future.json?key={os.getenv('WEATHER_API_TOKEN')}"

    url = f"{url_base_url}&q={location}&dt={date}"
    print(url)
    response = requests.request("GET", url)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA SaaS HW 1 Kolesnyk</h2></p>"


@app.route(
    "/weather",
    methods=["POST"],
)
def weather_endpoint():
    request_data = request.get_json()

    token = request_data['token']

    if token is None:
        raise InvalidUsage("token is required", status_code=400)
    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    request_name = request_data["request_name"]
    location = request_data["location"]
    date = request_data["date"]

    weather = get_weather(location, date)

    result = {
        "request_name": request_name,
        "timestamp": dt.datetime.now().isoformat(),
        "location": location,
        "date": date,
        "weather": weather
    }

    return result