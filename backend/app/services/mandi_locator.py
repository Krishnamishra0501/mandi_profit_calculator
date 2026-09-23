import pandas as pd
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

BASE_DIR = Path(__file__).resolve().parents[3]
CSV_PATH = BASE_DIR / "data" / "mandis.csv"

df = pd.read_csv(CSV_PATH)


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def get_nearest_mandis(latitude, longitude, limit=5):
    results = []

    for _, mandi in df.iterrows():
        distance = calculate_distance(
            latitude,
            longitude,
            mandi["latitude"],
            mandi["longitude"]
        )

        results.append({
            "mandi_name": mandi["mandi_name"],
            "district": mandi["district"],
            "state": mandi["state"],
            "latitude": mandi["latitude"],
            "longitude": mandi["longitude"],
            "distance_km": round(distance, 2)
        })

    results.sort(key=lambda x: x["distance_km"])

    return results[:limit]