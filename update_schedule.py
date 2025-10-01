import requests
import json
import os
import sys
from datetime import datetime, timezone, timedelta

# URL data jadwal Volleyball World
URL = "https://tv.volleyballworld.com/?_data=routes%2F_index"
OUTFILE_INDOOR = "indoor_live.json"
OUTFILE_BEACH = "beach_live.json"

# Konversi timestamp/ISO ke WIB
def to_wib(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        dt = dt.astimezone(timezone(timedelta(hours=7)))
        return dt.isoformat()
    except Exception:
        return dt_str

# Ambil data dari web
def fetch_schedule():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    data = r.json()
    # Data jadwal ada di "pageProps" → "liveEvents"
    events = data.get("pageProps", {}).get("liveEvents", [])
    return events

# Parsing dan membedakan indoor & beach
def parse_entries(entries):
    indoor = []
    beach = []

    for e in entries:
        title = e.get("title")
        media_id = e.get("id")
        ext = e.get("extensions", {})
        start = e.get("scheduled_start") or ext.get("VCH.ScheduledStart") or ext.get("match_date")
        if isinstance(start, str):
            start = to_wib(start)

        poster = None
        media_group = e.get("media_group", [])
        if media_group:
            imgs = media_group[0].get("media_item", [])
            if imgs:
                poster = imgs[-1]["src"]

        # Cari src HLS
        src = None
        for link in e.get("links", []):
            if link.get("type") == "application/vnd.apple.mpegurl":
                src = link.get("href")
                break
        if not src:
            src = f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8"

        entry = {
            "title": title,
            "start": start,
            "src": src,
            "poster": poster or f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920"
        }

        category = e.get("category", "").lower()
        if "beach" in category:
            beach.append(entry)
        else:
            indoor.append(entry)

    return indoor, beach

def save_if_updated(outfile, new_data):
    if os.path.exists(outfile):
        with open(outfile, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = []

    if old_data == new_data:
        print(f"⚡ Tidak ada update → skip {outfile}.")
        return False

    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    print(f"📊 Update tersimpan di {outfile} ({len(new_data)} jadwal).")
    return True

def main():
    try:
        entries = fetch_schedule()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

    indoor, beach = parse_entries(entries)

    updated_indoor = save_if_updated(OUTFILE_INDOOR, indoor)
    updated_beach = save_if_updated(OUTFILE_BEACH, beach)

    if not updated_indoor and not updated_beach:
        sys.exit(0)

if __name__ == "__main__":
    main()
