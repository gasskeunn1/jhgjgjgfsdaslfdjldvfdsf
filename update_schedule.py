import requests, json, os, sys
from datetime import datetime, timezone, timedelta

URL = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/FljcQiNy"
OUTFILE = "volleyball_schedule.json"

def fetch_schedule():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    return r.json()

def parse_entry(e):
    title = e.get("title")

    # Poster
    poster = None
    media_group = e.get("media_group", [])
    if media_group:
        imgs = media_group[0].get("media_item", [])
        if imgs:
            poster = imgs[-1].get("src")

    # Start time
    start = None
    ext = e.get("extensions", {})
    if e.get("scheduled_start"):
        start = e["scheduled_start"]
    elif ext.get("VCH.ScheduledStart"):
        start = ext.get("VCH.ScheduledStart")
    elif ext.get("match_date"):
        start = ext.get("match_date")
    elif "actions" in ext:
        for act in ext["actions"]:
            if act.get("type") == "add_to_calendar":
                ts = act.get("options", {}).get("startDate")
                if ts:
                    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                    start = dt.astimezone(timezone(timedelta(hours=7))).isoformat()
                    break

    # Konversi string ke WIB
    if isinstance(start, str):
        try:
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            dt = dt.astimezone(timezone(timedelta(hours=7)))
            start = dt.isoformat()
        except Exception:
            pass

    # Src
    src = None
    for link in e.get("links", []):
        if link.get("type") == "application/vnd.apple.mpegurl":
            src = link.get("href")
            break
    media_id = e.get("id") or "placeholder"
    if not src:
        src = f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8"
    if not poster:
        poster = f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920"

    return {
        "title": title,
        "start": start,
        "src": src,
        "poster": poster
    }

def parse_feeds(root):
    result = []
    feeds = root.get("serverLoadedFeeds", [])
    for feed in feeds:
        entries = feed.get("feed", {}).get("entry", [])
        for e in entries:
            result.append(parse_entry(e))
    return result

def main():
    try:
        data = fetch_schedule()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

    new_data = parse_feeds(data)

    # Cek update
    if os.path.exists(OUTFILE):
        with open(OUTFILE, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = []

    if old_data == new_data:
        print("⚡ Tidak ada update dari web sumber → skip workflow.")
        sys.exit(0)

    # Simpan JSON
    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"📊 Update tersimpan ({len(new_data)} jadwal).")

if __name__ == "__main__":
    main()
