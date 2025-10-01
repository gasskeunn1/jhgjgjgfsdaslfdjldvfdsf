import requests
import json
import os
import sys
from datetime import datetime, timezone, timedelta

URL = "https://tv.volleyballworld.com/?_data=routes%2F_index"
INDOOR_FILE = "indoor_live.json"
BEACH_FILE = "beach_live.json"

# zona waktu WIB
TZ = timezone(timedelta(hours=7))

def fetch_data():
    try:
        r = requests.get(URL, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

def parse_matches(data):
    indoor = []
    beach = []

    # asumsi data match ada di data["matches"]
    matches = data.get("matches", [])
    for m in matches:
        # ambil info dasar
        title = m.get("title") or m.get("match_title")
        start_ts = m.get("start") or m.get("scheduled_start")
        start = None
        if start_ts:
            try:
                dt = datetime.fromtimestamp(start_ts / 1000, tz=timezone.utc)
                start = dt.astimezone(TZ).isoformat()
            except:
                start = None

        # ambil poster
        poster = m.get("poster") or m.get("media_url")
        # ambil streaming link jika ada
        src = None
        links = m.get("links") or []
        for l in links:
            if l.get("type") == "application/vnd.apple.mpegurl":
                src = l.get("href")
                break

        media_id = m.get("id")
        if not src:
            src = f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8"
        if not poster:
            poster = f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920"

        entry = {
            "title": title,
            "start": start,
            "src": src,
            "poster": poster
        }

        discipline = m.get("discipline") or ""
        if "Beach" in discipline:
            beach.append(entry)
        else:
            indoor.append(entry)

    return indoor, beach

def save_if_changed(outfile, new_data):
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
    data = fetch_data()
    indoor, beach = parse_matches(data)
    updated = False
    updated |= save_if_changed(INDOOR_FILE, indoor)
    updated |= save_if_changed(BEACH_FILE, beach)

    if not updated:
        sys.exit(0)

if __name__ == "__main__":
    main()
