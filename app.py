from unittest import result

from flask import Flask, render_template, request, jsonify
from utils.route_engine import RouteEngine
from utils.station_network import STATIONS
from utils.ai_predictor import AIPredictor
import random

app = Flask(__name__)

# -----------------------------
# Demo Login Credentials
# -----------------------------
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    },
    "passenger": {
        "password": "pass123",
        "role": "passenger"
    }
}

# -----------------------------
# Global Simulation State
# -----------------------------
simulation_state = {
    "active_buses": [
        {
            "bus_id": "KA-850",
            "current_stop": "Domlur",
            "eta": "12 mins",
            "occupancy": "65%",
            "status": "On Time"
        },

        {
            "bus_id": "KA-839",
            "current_stop": "Whitefield",
            "eta": "13 mins",
            "occupancy": "82%",
            "status": "Moving"
        },

        {
            "bus_id": "KBS-88",
            "current_stop": "Vijayanagar",
            "eta": "10 mins",
            "occupancy": "54%",
            "status": "On Time"
        },

        {
            "bus_id": "KA-162",
            "current_stop": "Majestic",
            "eta": "18 mins",
            "occupancy": "91%",
            "status": "Delayed"
        },

        {
            "bus_id": "BMTC-451",
            "current_stop": "MG Road",
            "eta": "10 mins",
            "occupancy": "72%",
            "status": "Delayed"
        }
    ],

    "traffic_level": 3,

    "weather": "Clear",

    "special_event": False,

    "peak_hour": False,

    "emergency_mode": False
}

# -----------------------------
# Route Engine
# -----------------------------
engine = RouteEngine()
ai = AIPredictor()


# -----------------------------
# Pages
# -----------------------------
@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/passenger")
def passenger_page():
    return render_template(
        "passenger.html",
        stations=sorted(STATIONS.keys())
    )


@app.route("/admin")
def admin_page():
    return render_template("admin.html")


# -----------------------------
# Login API
# -----------------------------
@app.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data.get(
        "username", ""
    ).strip()

    password = data.get(
        "password", ""
    ).strip()

    user = USERS.get(username)

    if (
        user and
        user["password"] == password
    ):
        return jsonify({
            "success": True,
            "role": user["role"]
        })

    return jsonify({
        "success": False,
        "message":
        "Invalid credentials"
    })


# -----------------------------
# Route API
# -----------------------------
@app.route(
    "/get_route",
    methods=["POST"]
)
def get_route():

    data = request.json

    source = data.get(
        "source"
    )

    destination = data.get(
        "destination"
    )

    if source == destination:
        return jsonify({
            "success": False,
            "message":
            "Source and destination cannot be same"
        })

    result = engine.get_route_info(
        source,
        destination
    )

    if not result["success"]:
        return jsonify(result)

    peak_hour = random.choice(
        [0, 1]
    )

    passenger_density = (
        random.randint(30, 95)
    )

    historical_delay = (
        random.randint(0, 15)
    )

    avg_speed = (
        random.randint(25, 60)
    )

    peak_hour = random.choice(
        [0, 1]
    )

    passenger_density = random.randint(
        30,
        95
    )

    historical_delay = random.randint(
        0,
        15
    )

    avg_speed = random.randint(
        25,
        60
    )

    estimated_eta = ai.predict_eta(

        distance_km=
        result["distance_km"],

        traffic_level=
        simulation_state[
            "traffic_level"
        ],

        weather=
        simulation_state[
            "weather"
        ],

        peak_hour=
        peak_hour,

        special_event=
        int(
            simulation_state[
                "special_event"
            ]
        ),

        passenger_density=
        passenger_density,

        historical_delay=
        historical_delay,

        avg_speed=
        avg_speed
    )

    ai_confidence = random.randint(
        86,
        98
    )

    traffic = simulation_state[
        "traffic_level"
    ]

    weather = simulation_state[
        "weather"
    ]

    if (
        traffic >= 8
        or
        historical_delay >= 12
    ):

        delay_risk = "High"

    elif (
        traffic >= 5
        or
        weather == "Rain"
        or
        historical_delay >= 6
    ):

        delay_risk = "Medium"

    else:

        delay_risk = "Low"

    result.update({
            "predicted_eta":
            round(estimated_eta),

            "traffic_level":
            simulation_state[
                "traffic_level"
            ],

            "weather":
            simulation_state[
                "weather"
            ],

            "special_event":
            simulation_state[
                "special_event"
            ],

            "delay_risk":
            delay_risk,

            "ai_confidence":
            ai_confidence
        })
    route_coordinates = []

    for stop in result["route"]:

        if stop in STATIONS:

            lat, lng = STATIONS[stop]

            route_coordinates.append({

                "station": stop,

                "lat": lat,

                "lng": lng
            })

    result["route_coordinates"] = (
        route_coordinates
    )
    return jsonify(result)


# -----------------------------
# Admin Simulation API
# -----------------------------
@app.route(
    "/update_simulation",
    methods=["POST"]
)
def update_simulation():

    data = request.json

    simulation_state[
        "traffic_level"
    ] = int(
        data.get(
            "traffic_level",
            3
        )
    )

    simulation_state[
        "weather"
    ] = data.get(
        "weather",
        "Clear"
    )

    simulation_state[
        "special_event"
    ] = data.get(
        "special_event",
        False
    )

    return jsonify({
        "success": True,
        "state":
        simulation_state
    })


# -----------------------------
# Get Current Simulation State
# -----------------------------
@app.route(
    "/simulation_state"
)
def get_simulation_state():
    return jsonify(
        simulation_state
    )


# -----------------------------
# Get Stations
# -----------------------------
@app.route("/stations")
def get_stations():
    return jsonify({
        "stations":
        sorted(
            list(
                STATIONS.keys()
            )
        )
    })

@app.route("/get_active_buses")
def get_active_buses():
    return jsonify({
        "active_buses": simulation_state["active_buses"]
    })
# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )