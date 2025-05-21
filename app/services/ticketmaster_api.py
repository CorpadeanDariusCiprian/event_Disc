import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TICKET_MASTER_KEY")

print("Ticketmaster API Key:", API_KEY)
def search_events(keyword, category=None, date=None, address=None, limit=5):
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": API_KEY,
        "keyword": keyword,
        "size": limit,
    }

    if category:
        params["classificationName"] = category
    if address:
        params["city"] = address
    if date:
        params["startDateTime"] = date

    print(f"Requesting Ticketmaster API with params: {params}")

    response = requests.get(base_url, params=params)

    print(f"Response status: {response.status_code}")
    if response.status_code != 200:
        print("Ticketmaster API Error:", response.text)
        return []

    data = response.json()
    print(f"Response data keys: {list(data.keys())}")

    events = []

    if "_embedded" in data and "events" in data["_embedded"]:
        for item in data["_embedded"]["events"]:
            events.append({
                "name": item["name"],
                "date": item["dates"]["start"].get("localDate", ""),
                "time": item["dates"]["start"].get("localTime", ""),
                "venue": item["_embedded"]["venues"][0]["name"],
                "url": item.get("url", "")
            })
    else:
        print("No events found in the response.")

    return events

#if __name__ == "__main__":
    #events = search_events("Coldplay", address="London")
    #for event in events:
        #print(event)