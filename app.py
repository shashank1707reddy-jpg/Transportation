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
# Live Buses on Route API
# -----------------------------

# Persistent bus state so buses move smoothly across refreshes
_live_bus_state = {}

@app.route("/get_live_buses", methods=["POST"])
def get_live_buses():
    """
    Returns buses on the route heading from source to destination.
    Buses are spread across all segments of the route BEFORE the source stop
    (i.e. approaching the boarding point from behind on the network).
    On each call their progress advances so they appear to move.
    Since source is always idx 0 in Dijkstra output, we extend the route
    by finding graph neighbours that feed into the source stop, giving
    buses real stops to travel from before reaching the passenger.
    """
    data = request.json
    source = data.get("source")
    destination = data.get("destination")

    if not source or not destination:
        return jsonify({"success": False, "message": "Missing source or destination"})

    result = engine.get_route_info(source, destination)
    if not result["success"]:
        return jsonify({"success": False, "message": "No route found"})

    route = result["route"]  # [source, ..., destination]

    # Build approach corridor: graph neighbours of source not already in route
    from utils.station_network import GRAPH

    approach = []
    if source in GRAPH:
        for nb in GRAPH[source]:
            if nb not in route and nb in STATIONS:
                approach.append(nb)
    # One more hop out
    for a in list(approach):
        if a in GRAPH:
            for nb in GRAPH[a]:
                if nb not in route and nb not in approach and nb in STATIONS:
                    approach.append(nb)

    approach_chain = list(reversed(approach[:4])) + [source]
    full_path = approach_chain + route[1:]   # [approach... source ... destination]
    source_idx = len(approach_chain) - 1     # index of source in full_path

    statuses = ["Moving", "On Time", "Approaching", "Delayed"]
    prefixes = ["500D", "KBS", "VJ", "BMTC", "EXP", "KA"]
    state_key = f"{source}|{destination}"

    # Initialise persistent bus states on first call
    if state_key not in _live_bus_state:
        buses = []
        num_buses = random.randint(4, 6)
        total_segs = len(full_path) - 1
        for i in range(num_buses):
            # Spread evenly across ALL segments so each bus is on a different one
            seg_idx = int(i * total_segs / num_buses)
            seg_idx = max(0, min(seg_idx, total_segs - 1))
            buses.append({
                "bus_id": f"{random.choice(prefixes)}-{random.randint(10, 999)}",
                "seg_idx": seg_idx,
                "progress": random.uniform(0.1, 0.7),
                "speed_kmh": random.randint(20, 50),
                "occupancy": random.randint(20, 92),
                "status": random.choice(statuses),
            })
        _live_bus_state[state_key] = {"buses": buses, "path": full_path, "source_idx": source_idx}

    state = _live_bus_state[state_key]
    full_path = state["path"]
    source_idx = state["source_idx"]  # index of source in full_path
    live_buses = []

    for bus in state["buses"]:
        seg_idx = bus["seg_idx"]
        progress = bus["progress"]

        # Advance progress (simulate movement between API calls)
        speed_fraction = bus["speed_kmh"] / 100.0 * random.uniform(0.08, 0.18)
        progress += speed_fraction

        if progress >= 1.0:
            # Move to next segment
            seg_idx = (seg_idx + 1) % (len(full_path) - 1)
            progress = 0.0
            bus["status"] = random.choice(statuses)

        bus["seg_idx"] = seg_idx
        bus["progress"] = progress

        stop_a = full_path[seg_idx]
        stop_b = full_path[min(seg_idx + 1, len(full_path) - 1)]

        if stop_a not in STATIONS or stop_b not in STATIONS:
            continue

        lat_a, lng_a = STATIONS[stop_a]
        lat_b, lng_b = STATIONS[stop_b]

        lat = lat_a + (lat_b - lat_a) * progress
        lng = lng_a + (lng_b - lng_a) * progress

        # ETA to source: segments remaining before source_idx
        segs_to_source = max(0, source_idx - seg_idx) + (1 - progress)
        eta_to_source = max(1, round(segs_to_source * random.uniform(3, 7)))

        live_buses.append({
            "bus_id": bus["bus_id"],
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "current_stop": stop_a,
            "next_stop": stop_b,
            "seg_idx": seg_idx,
            "progress": round(progress, 3),
            "eta_to_source": eta_to_source,
            "occupancy": bus["occupancy"],
            "status": bus["status"],
            "speed": bus["speed_kmh"]
        })

    return jsonify({
        "success": True,
        "route": route,
        "full_path": full_path,
        "source": source,
        "destination": destination,
        "source_idx": source_idx,
        "live_buses": live_buses
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