import requests, json, os, sys
from datetime import datetime, timezone, timedelta

URL = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/FljcQiNy"
INDOOR_FILE = "indoor_live.json"
BEACH_FILE = "beach_live.json"

def fetch_schedule():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    data = r.json()
    return data.get("entry", [])

def parse_entries(entries):
    result = []
    for e in entries:
        title = e.get("title", "")
        media_id = e.get("id")

        # ambil link HLS
        src = None
        for link in e.get("links", []):
            if link.get("type") == "application/vnd.apple.mpegurl":
                src = link.get("href")
                break

        # ambil poster
        poster = None
        media_group = e.get("media_group", [])
        if media_group:
            imgs = media_group[0].get("media_item", [])
            if imgs:
                poster = imgs[-1]["src"]

        # ambil waktu mulai
        start = e.get("scheduled_start")
        if isinstance(start, str):
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                dt = dt.astimezone(timezone(timedelta(hours=7)))
                start = dt.isoformat()
            except:
                pass

        result.append({
            "title": title,
            "start": start,
            "src": src or f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8",
            "poster": poster or f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920"
        })
    return result

def save_json(filename, data):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = []
    if old_data == data:
        print(f"⚡ Tidak ada update → skip {filename}.")
        return
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📊 Update tersimpan di {filename} ({len(data)} jadwal).")

def main():
    try:
        entries = fetch_schedule()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

    all_data = parse_entries(entries)

    # Pisahkan indoor dan beach
    indoor = [x for x in all_data if "indoor" in x["title"].lower()]
    beach = [x for x in all_data if "beach" in x["title"].lower()]

    save_json(INDOOR_FILE, indoor)
    save_json(BEACH_FILE, beach)

if __name__ == "__main__":
    main()
