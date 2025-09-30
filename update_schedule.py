import requests
import json
import hashlib
import os
from datetime import datetime, timezone, timedelta

URL = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/FljcQiNy"
OUTPUT = "volleyballworld.json"

def fetch_matches():
    resp = requests.get(URL)
    data = resp.json()

    matches = []
    for entry in data.get("playlist", []):
        start_time = entry.get("VCH.ScheduledStart")
        if not start_time:
            continue

        # ubah ke zona waktu +07:00
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        start_local = start_dt.astimezone(timezone(timedelta(hours=7)))

        match = {
            "title": entry.get("title"),
            "start": start_local.isoformat(),
            "src": None,
            "poster": entry.get("image")
        }

        # kalau status LIVE → isi src dengan m3u8
        if str(entry.get("VCH.EventState")).upper() == "LIVE" and entry.get("file"):
            match["src"] = entry.get("file")

        matches.append(match)

    return matches

def file_hash(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def save_json(matches):
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    new_data = fetch_matches()
    new_hash = hashlib.md5(json.dumps(new_data, sort_keys=True).encode()).hexdigest()
    old_hash = file_hash(OUTPUT)

    if new_hash != old_hash:
        save_json(new_data)
        print("✅ JSON diperbarui, mengikuti web sumber.")
        exit(0)
    else:
        print("⚡ Tidak ada perubahan, skip update.")
        exit(78)
