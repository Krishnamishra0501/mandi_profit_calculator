import os
import json
import subprocess
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DATA_GOV_API_KEY")

BASE_URL = (
    "https://api.data.gov.in/resource/"
    "35985678-0d79-46b4-9ed6-6f13308a1d24"
)

BASE_DIR = Path(__file__).resolve().parents[3]
CSV_PATH = BASE_DIR / "data" / "mandi_prices.csv"

df = pd.read_csv(CSV_PATH)

df.columns = [
    "state",
    "district",
    "market",
    "commodity",
    "variety",
    "grade",
    "arrival_date",
    "min_price",
    "max_price",
    "modal_price"
]

for col in ["state", "district", "market", "commodity"]:
    df[col] = df[col].astype(str).str.strip()


def get_api_prices(
    state=None,
    district=None,
    commodity=None,
    arrival_date=None
):
    url = (
        BASE_URL
        + "?api-key=" + API_KEY
        + "&format=json"
        + "&limit=100"
    )

    if state:
        url += "&filters%5BState%5D=" + state.strip()

    if district:
        url += "&filters%5BDistrict%5D=" + district.strip()

    if commodity:
        url += "&filters%5BCommodity%5D=" + commodity.strip()

    if arrival_date:
        url += "&filters%5BArrival_Date%5D=" + arrival_date.strip()

    try:
        result = subprocess.run(
            [
                "curl.exe",
                "-s",
                "--max-time",
                "30",
                url
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("CURL ERROR:", result.stderr)
            return []

        data = json.loads(result.stdout)

        if data.get("records"):
            print("DATA GOV API SUCCESS")
            print("TOTAL:", data.get("total"))
            print("RETURNED:", len(data["records"]))

            return data["records"]

        print("API RESPONSE:", data)

        return []

    except Exception as e:
        print("API ERROR:", repr(e))
        return []


async def get_prices(
    state=None,
    district=None,
    commodity=None,
    arrival_date=None
):
    records = get_api_prices(
        state=state,
        district=district,
        commodity=commodity,
        arrival_date=arrival_date
    )

    if records:
        return records

    return get_csv_prices(
        state=state,
        district=district,
        commodity=commodity
    )


def get_csv_prices(
    state=None,
    district=None,
    commodity=None
):
    result = df.copy()

    if state:
        result = result[
            result["state"].str.lower()
            == state.strip().lower()
        ]

    if district:
        result = result[
            result["district"].str.lower()
            == district.strip().lower()
        ]

    if commodity:
        result = result[
            result["commodity"].str.lower()
            == commodity.strip().lower()
        ]

    return result.to_dict(orient="records")