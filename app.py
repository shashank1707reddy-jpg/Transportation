from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from utils.route_engine import RouteEngine
from utils.station_network import STATIONS
from utils.ai_predictor import AIPredictor
from werkzeug.security import generate_password_hash, check_password_hash
import random, json, os, re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "bmtc_transit_secret_2024_xK9#mP"

# -----------------------------
# Admin Credentials (fixed)
# -----------------------------
ADMIN_CREDENTIALS = {
    "username": "bmtc_admin",
    "password": generate_password_hash("Admin@BMTC#2024"),
    "role": "admin"
}

# -----------------------------
# Passenger DB (JSON file)
# -----------------------------
PASSENGER_DB = os.path.join(os.path.dirname(__file__), "passengers.json")

def load_passengers():
    if not os.path.exists(PASSENGER_DB):
        return {}
    with open(PASSENGER_DB, "r") as f:
        return json.load(f)

def save_passengers(db):
    with open(PASSENGER_DB, "w") as f:
        json.dump(db, f, indent=2)

def is_valid_phone(phone):
    return bool(re.match(r"^[6-9]\d{9}$", phone))

def is_valid_dob(dob):
    try:
        dt = datetime.strptime(dob, "%Y-%m-%d")
        age = (datetime.today() - dt).days // 365
        return age >= 5
    except:
        return False

# -----------------------------
# Session helpers
# -----------------------------
def passenger_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "passenger":
            return redirect(url_for("passenger_login_page"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("admin_login_page"))
        return f(*args, **kwargs)
    return decorated

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

    "emergency_mode": False,

    "active_bus_count": 42,

    "passengers_today": 13482
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
def index():
    return redirect(url_for("passenger_login_page"))

# ---- Passenger Auth ----
@app.route("/passenger/login")
def passenger_login_page():
    if session.get("role") == "passenger":
        return redirect(url_for("passenger_page"))
    return render_template("passenger_login.html")

@app.route("/passenger/register")
def passenger_register_page():
    return render_template("passenger_register.html")

@app.route("/passenger/register", methods=["POST"])
def passenger_register():
    data = request.json
    name     = data.get("name", "").strip()
    phone    = data.get("phone", "").strip()
    dob      = data.get("dob", "").strip()
    password = data.get("password", "").strip()

    if not all([name, phone, dob, password]):
        return jsonify({"success": False, "message": "All fields are required."})
    if not is_valid_phone(phone):
        return jsonify({"success": False, "message": "Enter a valid 10-digit Indian mobile number."})
    if not is_valid_dob(dob):
        return jsonify({"success": False, "message": "Enter a valid date of birth."})
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."})

    db = load_passengers()
    if phone in db:
        return jsonify({"success": False, "message": "An account with this phone number already exists."})

    db[phone] = {
        "name": name,
        "phone": phone,
        "dob": dob,
        "password": generate_password_hash(password),
        "created_at": datetime.now().isoformat()
    }
    save_passengers(db)
    return jsonify({"success": True, "message": "Account created! Please log in."})

@app.route("/passenger/login", methods=["POST"])
def passenger_login():
    data     = request.json
    phone    = data.get("phone", "").strip()
    password = data.get("password", "").strip()

    if not phone or not password:
        return jsonify({"success": False, "message": "Phone and password are required."})

    db = load_passengers()
    user = db.get(phone)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Invalid phone number or password."})

    session["role"]  = "passenger"
    session["phone"] = phone
    session["name"]  = user["name"]
    return jsonify({"success": True})

@app.route("/passenger/logout")
def passenger_logout():
    session.clear()
    return redirect(url_for("passenger_login_page"))

# ---- Admin Auth ----
@app.route("/admin/login")
def admin_login_page():
    if session.get("role") == "admin":
        return redirect(url_for("admin_page"))
    return render_template("admin_login.html")

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data     = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if (username == ADMIN_CREDENTIALS["username"] and
            check_password_hash(ADMIN_CREDENTIALS["password"], password)):
        session["role"]     = "admin"
        session["username"] = username
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Invalid admin credentials."})

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login_page"))

# ---- Protected Pages ----
@app.route("/passenger")
@passenger_required
def passenger_page():
    return render_template(
        "passenger.html",
        stations=sorted(STATIONS.keys()),
        name=session.get("name", "Passenger")
    )

@app.route("/admin")
@admin_required
def admin_page():
    return render_template("admin.html")


# -----------------------------
# Route API
# -----------------------------
@app.route(
    "/get_route",
    methods=["POST"]
)
@passenger_required
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
@admin_required
def update_simulation():

    data = request.json

    traffic_level = int(
        data.get(
            "traffic_level",
            3
        )
    )

    weather = data.get(
        "weather",
        "Clear"
    )

    special_event = data.get(
        "special_event",
        False
    )

    peak_hour = data.get(
        "peak_hour",
        False
    )

    emergency_mode = data.get(
        "emergency_mode",
        False
    )

    simulation_state["traffic_level"]  = traffic_level
    simulation_state["weather"]        = weather
    simulation_state["special_event"]  = special_event
    simulation_state["peak_hour"]      = peak_hour
    simulation_state["emergency_mode"] = emergency_mode

    # -----------------------------
    # Ask the TRAINED MODEL (from your dataset) what ETA
    # looks like system-wide under these exact conditions.
    # We use a fixed "average city trip" profile (the dataset's
    # median distance/density/speed/delay) so only the admin's
    # live controls (traffic, weather, peak, event) vary the result.
    # The model was trained only on Clear/Rain/Fog, so Storm is
    # mapped to Rain (its closest trained equivalent) for the model
    # call, then a small extra penalty is layered on top.
    # -----------------------------
    model_weather = weather if weather in ("Clear", "Rain", "Fog") else "Rain"

    predicted_eta = ai.predict_eta(
        distance_km=15.0,          # dataset's typical mid-range trip
        traffic_level=traffic_level,
        weather=model_weather,
        peak_hour=1 if peak_hour else 0,
        special_event=1 if special_event else 0,
        passenger_density=60,      # dataset's typical density
        historical_delay=5,        # dataset's typical historical delay
        avg_speed=40               # dataset's typical avg speed
    )

    if weather == "Storm":
        predicted_eta += 6  # extra penalty for the untrained condition

    simulation_state["model_predicted_eta"] = predicted_eta

    # -----------------------------
    # Derive Active Bus Count FROM the model's ETA
    # -----------------------------
    # Dataset's predicted_eta ranges ~12 (best case) to ~138 (worst case),
    # mean ~75. We map that range onto a realistic city fleet size:
    # best case (low ETA, smooth conditions) -> more buses can keep
    # routes moving efficiently; worst case (high ETA, gridlock) ->
    # fewer buses can complete circuits, so effective active count drops.
    ETA_MIN, ETA_MAX = 12.0, 138.0
    eta_clamped = max(ETA_MIN, min(ETA_MAX, predicted_eta))
    severity = (eta_clamped - ETA_MIN) / (ETA_MAX - ETA_MIN)  # 0 (best) -> 1 (worst)

    FLEET_MAX, FLEET_MIN = 55, 12
    active_bus_count = round(FLEET_MAX - severity * (FLEET_MAX - FLEET_MIN))

    # Special event / peak hour pull a few extra reserve buses onto
    # the road on top of the ETA-driven baseline, emergency mode pulls
    # buses off for safety.
    if peak_hour:
        active_bus_count += 4
    if special_event:
        active_bus_count += 3
    if emergency_mode:
        active_bus_count = round(active_bus_count * 0.6)

    active_bus_count = max(8, min(60, active_bus_count))
    simulation_state["active_bus_count"] = active_bus_count

    # -----------------------------
    # Derive Passengers Today FROM the model's ETA + bus count
    # -----------------------------
    # Worse predicted ETA (severity closer to 1) means slower trips,
    # so fewer completed trips per bus per day -> fewer riders served,
    # even though more people may be *waiting*. Better ETA means buses
    # complete more circuits and serve more riders.
    trips_per_bus_per_day = round(14 - severity * 8)  # 14 (fast day) -> 6 (gridlock day)
    riders_per_trip = 45

    passengers_today = active_bus_count * trips_per_bus_per_day * riders_per_trip

    if peak_hour:
        passengers_today = round(passengers_today * 1.25)
    if special_event:
        passengers_today = round(passengers_today * 1.15)
    if emergency_mode:
        passengers_today = round(passengers_today * 0.5)

    simulation_state["passengers_today"] = passengers_today

    return jsonify({
        "success": True,
        "state": simulation_state,
        "active_bus_count": active_bus_count,
        "passengers_today": passengers_today,
        "model_predicted_eta": predicted_eta
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
@passenger_required
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
@passenger_required
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