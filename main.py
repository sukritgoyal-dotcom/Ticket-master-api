from fastapi import FastAPI
import requests
import os

app = FastAPI(title="Ticketmaster Events API")

TM_API_KEY = os.getenv("TM_API_KEY")
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"


@app.get("/")
def home():
    return {"status": "API is running"}


@app.get("/events")
def get_events(
    city: str = None,
    state: str = None,
    lat: float = None,
    lon: float = None,
    radius: int = 25,
    start_date: str = None,
    end_date: str = None,
    size: int = 50
):
    params = {
        "apikey": TM_API_KEY,
        "radius": radius,
        "unit": "miles",
        "size": size
    }

    if city:
        params["city"] = city
    if state:
        params["stateCode"] = state
    if lat and lon:
        params["latlong"] = f"{lat},{lon}"

    if start_date:
        params["startDateTime"] = f"{start_date}T00:00:00Z"
    if end_date:
        params["endDateTime"] = f"{end_date}T23:59:59Z"

    r = requests.get(BASE_URL, params=params)
    data = r.json()

    events = []

    if "_embedded" in data:
        for e in data["_embedded"]["events"]:
            venue = e["_embedded"]["venues"][0]

            events.append({
                "event_name": e["name"],
                "date": e["dates"]["start"].get("localDate"),
                "time": e["dates"]["start"].get("localTime"),
                "venue": venue["name"],
                "city": venue["city"]["name"],
                "state": venue["state"]["stateCode"],
                "category": e["classifications"][0]["segment"]["name"],
                "url": e["url"]
            })

    return {"count": len(events), "events": events}
