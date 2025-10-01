import requests
import json
import os
import sys
from datetime import datetime, timezone, timedelta

URL = "https://tv.volleyballworld.com/?_data=routes%2F_index"

INDOOR_FILE = "indoor_live.json"
BEACH_FILE = "beach_live.json"

def fetch_schedule():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    data = r.json()
    # Ambil daftar match
    matches = data.get("props", {}).get("pageProps", {}).get("schedule", {}).get("matches", [])
    return matches

def parse_matches(matches):
    indoor = []
    beach = []

    for m in matches:
        title = m.get("title") or m.get("match_name")
        start = m.get("startDateTime")
        if start:
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                dt = dt.astimezone(timezone(timedelta(hours=7)))  # WIB
                start = dt.isoformat()
            except Exception:
                pass

        # Buat link streaming default jika ada mediaId
        media_id = m.get("id")
        src = m.get("streamUrl") or f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8"
        poster = m.get("poster") or f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920"

        item = {
            "title": title,
            "start": start,
            "src": src,
            "poster": poster
        }

        discipline = m.get("tournament", {}).get("discipline", "").upper()
        if discipline == "BEACH":
            beach.append(item)
        else:
            indoor.append(item)

    return indoor, beach

def save_if_changed(filename, new_data):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = []

    if old_data == new_data:
        print(f"⚡ Tidak ada update → skip {filename}.")
        return False

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    print(f"📊 Update tersimpan di {filename} ({len(new_data)} jadwal).")
    return True

def main():
    try:
        matches = fetch_schedule()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

    indoor, beach = parse_matches(matches)

    save_if_changed(INDOOR_FILE, indoor)
    save_if_changed(BEACH_FILE, beach)

if __name__ == "__main__":
    main()
