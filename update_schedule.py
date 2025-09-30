import requests, json, os, sys
from datetime import datetime, timezone, timedelta

URL = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/FljcQiNy"
OUTFILE = "volleyballworld.json"

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
        start = ext.get("VCH.ScheduledStart")

        # convert UTC -> WIB (+7)
        if start:
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            dt = dt.astimezone(timezone(timedelta(hours=7)))
            start = dt.isoformat()

        # ambil JWPlayer id
        media_id = e["id"]

        # bikin src format live.isml/.m3u8
        src = f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8"

        result.append({
            "title": title,
            "start": start,
            "src": src,
            "poster": f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920"
        })
    return result

def main():
    entries = fetch_schedule()
    new_data = parse_entries(entries)

    if os.path.exists(OUTFILE):
        with open(OUTFILE, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = None

    if old_data == new_data:
        print("⚡ Tidak ada update dari web sumber → skip workflow.")
        sys.exit(0)

    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"📊 Update tersimpan ({len(new_data)} jadwal).")

if __name__ == "__main__":
    main()
