import json
import requests

# URL JSON web source (contoh: endpoint yang explore_vbworld.py gunakan)
URL = "https://tv.volleyballworld.com/?_data=routes%2F_index"  # ganti sesuai endpoint terbaru

# Fetch data dari web
response = requests.get(URL)
data = responsimport requests, json, os, sys
from datetime import datetime, timezone, timedelta

URL = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/FljcQiNy"
OUTFILE_INDOOR = "indoor_live.json"
OUTFILE_BEACH = "beach_live.json"

def fetch_schedule():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    data = r.json()
    return data.get("entry", [])

def parse_entries(entries):
    result = []
    for e in entries:
        title = e.get("title")

        poster = None
        media_group = e.get("media_group", [])
        if media_group:
            imgs = media_group[0].get("media_item", [])
            if imgs:
                poster = imgs[-1]["src"]

        ext = e.get("extensions", {})
        start = (
            e.get("scheduled_start") or
            ext.get("VCH.ScheduledStart") or
            ext.get("match_date")
        )

        if not start and "actions" in ext:
            for act in ext.get("actions", []):
                if act.get("type") == "add_to_calendar":
                    ts = act.get("options", {}).get("startDate")
                    if ts:
                        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                        start = dt.isoformat()
                        break

        if isinstance(start, str):
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                dt = dt.astimezone(timezone(timedelta(hours=7)))
                start = dt.isoformat()
            except Exception:
                pass

        src = None
        for link in e.get("links", []):
            if link.get("type") == "application/vnd.apple.mpegurl":
                src = link.get("href")
                break

        media_id = e.get("id")

        result.append({
            "title": title,
            "start": start,
            "src": src or f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8",
            "poster": poster or f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920",
            "type": "beach" if "beach" in (title or "").lower() else "indoor"
        })
    return result

def save_if_changed(filename, data):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = []

    if old_data == data:
        print(f"⚡ {filename} tidak berubah → skip.")
        return False

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📊 {filename} update tersimpan ({len(data)} jadwal).")
    return True

def main():
    try:
        entries = fetch_schedule()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

    parsed = parse_entries(entries)

    indoor = [e for e in parsed if e["type"] == "indoor"]
    beach = [e for e in parsed if e["type"] == "beach"]

    changed_indoor = save_if_changed(OUTFILE_INDOOR, indoor)
    changed_beach = save_if_changed(OUTFILE_BEACH, beach)

    if not (changed_indoor or changed_beach):
        print("⚡ Tidak ada update dari web sumber → skip workflow.")

if __name__ == "__main__":
    main()
e.json()

# Fungsi ekstrak feed menjadi list pertandingan
def extract_feed(feed):
    matches = []
    for entry in feed.get("entry", []):
        match = {}
        match["title"] = entry.get("title") or entry.get("extensions", {}).get("actions", [{}])[0].get("options", {}).get("title")
        match["src"] = entry.get("extensions", {}).get("actions", [{}])[0].get("options", {}).get("url", None)
        match["start"] = entry.get("extensions", {}).get("actions", [{}])[0].get("options", {}).get("startTime", None)
        matches.append(match)
    return matches

# Indoor feed → serverLoadedFeeds[1]
indoor_feed = data["serverLoadedFeeds"][1]["feed"]
indoor_matches = extract_feed(indoor_feed)

# Beach feed → serverLoadedFeeds[2]
beach_feed = data["serverLoadedFeeds"][2]["feed"]
beach_matches = extract_feed(beach_feed)

# Simpan ke file JSON
with open("indoor_live.json", "w", encoding="utf-8") as f:
    json.dump(indoor_matches, f, ensure_ascii=False, indent=4)

with open("beach_live.json", "w", encoding="utf-8") as f:
    json.dump(beach_matches, f, ensure_ascii=False, indent=4)

print("✅ indoor_live.json & beach_live.json berhasil dibuat!")
