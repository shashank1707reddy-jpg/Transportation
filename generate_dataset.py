import pandas as pd
import random
from utils.station_network import GRAPH

# -------------------------
# Settings
# -------------------------
NUM_SAMPLES = 30000

WEATHER_TYPES = [
    "Clear",
    "Rain",
    "Fog"
]

TIME_PERIODS = [
    "Morning",
    "Afternoon",
    "Evening",
    "Night"
]


# -------------------------
# Estimate Distance
# -------------------------
def get_random_distance():

    return round(
        random.uniform(2, 35),
        2
    )


# -------------------------
# ETA Logic (Ground Truth)
# -------------------------
def generate_eta(
    distance,
    traffic,
    weather,
    peak_hour,
    event,
    density,
    historical_delay
):

    base_eta = distance * 1.8

    traffic_penalty = (
        traffic * 2.5
    )

    weather_penalty = 0

    if weather == "Rain":
        weather_penalty = 8

    elif weather == "Fog":
        weather_penalty = 5

    peak_penalty = (
        10 if peak_hour
        else 0
    )

    event_penalty = (
        12 if event
        else 0
    )

    density_penalty = (
        density * 0.08
    )

    final_eta = (

        base_eta +

        traffic_penalty +

        weather_penalty +

        peak_penalty +

        event_penalty +

        density_penalty +

        historical_delay

    )

    noise = random.uniform(
        -2,
        2
    )

    return round(
        final_eta + noise,
        2
    )


# -------------------------
# Dataset Creation
# -------------------------
def create_dataset():

    stations = list(
        GRAPH.keys()
    )

    rows = []

    for _ in range(
        NUM_SAMPLES
    ):

        source = random.choice(
            stations
        )

        destination = (
            random.choice(
                stations
            )
        )

        while (
            source ==
            destination
        ):
            destination = (
                random.choice(
                    stations
                )
            )

        distance = (
            get_random_distance()
        )

        traffic_level = (
            random.randint(
                1,
                10
            )
        )

        weather = (
            random.choice(
                WEATHER_TYPES
            )
        )

        time_period = (
            random.choice(
                TIME_PERIODS
            )
        )

        peak_hour = (
            1 if
            time_period in [
                "Morning",
                "Evening"
            ]
            else 0
        )

        special_event = (
            random.choice(
                [0, 1]
            )
        )

        passenger_density = (
            random.randint(
                20,
                100
            )
        )

        historical_delay = (
            random.randint(
                0,
                15
            )
        )

        avg_speed = (
            random.randint(
                20,
                60
            )
        )

        eta = generate_eta(

            distance,

            traffic_level,

            weather,

            peak_hour,

            special_event,

            passenger_density,

            historical_delay
        )

        rows.append({

            "distance_km":
            distance,

            "traffic_level":
            traffic_level,

            "weather":
            weather,

            "peak_hour":
            peak_hour,

            "special_event":
            special_event,

            "passenger_density":
            passenger_density,

            "historical_delay":
            historical_delay,

            "avg_speed":
            avg_speed,

            "predicted_eta":
            eta
        })

    df = pd.DataFrame(
        rows
    )

    df.to_csv(

        "data/transit_dataset.csv",

        index=False
    )

    print(
        "Dataset generated!"
    )

    print(
        f"Rows: {len(df)}"
    )


if __name__ == "__main__":
    create_dataset()