import pandas as pd
import joblib

from sklearn.model_selection import (
    train_test_split
)

from sklearn.ensemble import (
    RandomForestRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    r2_score
)

from sklearn.preprocessing import (
    LabelEncoder
)

# -------------------------
# Load Dataset
# -------------------------
df = pd.read_csv(
    "data/transit_dataset.csv"
)

print(
    "Dataset Loaded"
)

# -------------------------
# Encode Weather
# -------------------------
weather_encoder = (
    LabelEncoder()
)

df["weather"] = (
    weather_encoder.fit_transform(
        df["weather"]
    )
)

# -------------------------
# Features / Target
# -------------------------
X = df[[
    "distance_km",
    "traffic_level",
    "weather",
    "peak_hour",
    "special_event",
    "passenger_density",
    "historical_delay",
    "avg_speed"
]]

y = df[
    "predicted_eta"
]

# -------------------------
# Train/Test Split
# -------------------------
X_train, X_test, y_train, y_test = (

    train_test_split(

        X,
        y,

        test_size=0.2,

        random_state=42
    )
)

# -------------------------
# Train Model
# -------------------------
model = RandomForestRegressor(

    n_estimators=120,

    max_depth=12,

    random_state=42,

    n_jobs=-1
)

print(
    "Training model..."
)

model.fit(
    X_train,
    y_train
)

print(
    "Training complete!"
)

# -------------------------
# Evaluation
# -------------------------
predictions = model.predict(
    X_test
)

mae = mean_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)

print(
    f"MAE: {mae:.2f}"
)

print(
    f"Accuracy (R²): {r2:.4f}"
)

# -------------------------
# Save Model
# -------------------------
joblib.dump(
    model,
    "models/transit_ai.joblib"
)

joblib.dump(
    weather_encoder,
    "models/weather_encoder.joblib"
)

print(
    "Model Saved!"
)