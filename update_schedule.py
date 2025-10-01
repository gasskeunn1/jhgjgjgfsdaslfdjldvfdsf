import requests
import json
import os
from datetime import datetime, timezone, timedelta

URL = "https://tv.volleyballworld.com/?_data=routes%2F_index"
OUTDIR = "schedules"

def fetch_data():
    response = requests.get(URL, timeout=20)
    response.raise_for_status()
    return response.json()

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📊 Data tersimpan ke {path} ({len(data)} item)")

def parse_match_data(data):
    indoor, beach = [], []
    for match in data.get("matches", []):
        title = match.get("title")
        start = match.get("startTime")
        src = match.get("streamUrl")
        poster = match.get("posterUrl")
        comp_type = match.get("competitionType", "").lower()

        match_info = {
            "title": title,
            "start": start,
            "src": src,
            "poster": poster
        }

        if "beach" in comp_type:
            beach.append(match_info)
        else:
            indoor.append(match_info)

    return indoor, beach

def main():
    data = fetch_data()
    indoor, beach = parse_match_data(data)
    save_json(f"{OUTDIR}/indoor_live.json", indoor)
    save_json(f"{OUTDIR}/beach_live.json", beach)

if __name__ == "__main__":
    main()
