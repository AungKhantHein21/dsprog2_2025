import requests
from datetime import datetime
from db import create_table, insert_weather, get_all_weather

JMA_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json"

def fetch_and_store_weather():
    response = requests.get(JMA_URL)
    data = response.json()

    saved_time = datetime.now().isoformat()

    for area_data in data[0]["timeSeries"][0]["areas"]:
        area = area_data["area"]["name"]
        weathers = area_data["weathers"]
        dates = data[0]["timeSeries"][0]["timeDefines"]

        for date, weather in zip(dates, weathers):
            insert_weather(area, date, weather, saved_time)

def show_weather():
    rows = get_all_weather()
    for r in rows:
        print(f"Area: {r[0]} | Date: {r[1]} | Weather: {r[2]}")

if __name__ == "__main__":
    create_table()
    fetch_and_store_weather()
    show_weather()
