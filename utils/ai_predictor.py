import joblib
import pandas as pd


class AIPredictor:

    def __init__(self):

        self.model = joblib.load(
            "models/transit_ai.joblib"
        )

        self.weather_encoder = (
            joblib.load(
                "models/weather_encoder.joblib"
            )
        )

    def predict_eta(

        self,

        distance_km,

        traffic_level,

        weather,

        peak_hour,

        special_event,

        passenger_density,

        historical_delay,

        avg_speed
    ):

        weather_encoded = (
            self.weather_encoder
            .transform(
                [weather]
            )[0]
        )

        input_data = pd.DataFrame([{

            "distance_km":
            distance_km,

            "traffic_level":
            traffic_level,

            "weather":
            weather_encoded,

            "peak_hour":
            peak_hour,

            "special_event":
            special_event,

            "passenger_density":
            passenger_density,

            "historical_delay":
            historical_delay,

            "avg_speed":
            avg_speed
        }])

        prediction = (
            self.model.predict(
                input_data
            )[0]
        )

        return round(
            prediction,
            2
        )