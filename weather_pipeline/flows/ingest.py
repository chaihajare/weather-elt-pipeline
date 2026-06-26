import requests
import duckdb
import pandas as pd
from prefect import flow, task
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = "weather_data.duckdb"

CITIES = {
    "Munich":      {"latitude": 48.1351, "longitude": 11.5820},
    "Berlin":      {"latitude": 52.5200, "longitude": 13.4050},
    "Hamburg":     {"latitude": 53.5488, "longitude": 9.9872},
    "Frankfurt":   {"latitude": 50.1109, "longitude": 8.6821},
    "Stuttgart":   {"latitude": 48.7758, "longitude": 9.1829},
}

@task(name="fetch_weather", retries=3, retry_delay_seconds=10)
def fetch_weather(city: str, lat: float, lon: float) -> pd.DataFrame:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "sunrise",
            "sunset",
        ],
        "timezone": "Europe/Berlin",
        "past_days": 7,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["daily"])
    df["city"] = city
    df["latitude"] = lat
    df["longitude"] = lon
    df["ingested_at"] = datetime.utcnow()
    df.rename(columns={"time": "date"}, inplace=True)
    return df

@task(name="load_to_duckdb")
def load_to_duckdb(df: pd.DataFrame):
    con = duckdb.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_weather (
            date VARCHAR,
            temperature_2m_max DOUBLE,
            temperature_2m_min DOUBLE,
            precipitation_sum DOUBLE,
            windspeed_10m_max DOUBLE,
            sunrise VARCHAR,
            sunset VARCHAR,
            city VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            ingested_at TIMESTAMP
        )
    """)
    con.execute("INSERT INTO raw_weather SELECT * FROM df")
    count = con.execute("SELECT COUNT(*) FROM raw_weather").fetchone()[0]
    con.close()
    print(f"Loaded {len(df)} rows. Total rows in DB: {count}")

@flow(name="weather-ingestion-flow")
def weather_ingestion_flow():
    for city, coords in CITIES.items():
        df = fetch_weather(city, coords["latitude"], coords["longitude"])
        load_to_duckdb(df)
        print(f"Done: {city} — {len(df)} rows")

if __name__ == "__main__":
    weather_ingestion_flow()