import requests, json, os, sys, re
from datetime import datetime, timezone, timedelta

URL = "https://tv.volleyballworld.com/schedule"

def fetch_schedule():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    return r.json()

def sanitize_filename(name: str) -> str:
    # ganti spasi/tanda baca dengan underscore, huruf kecil semua
    safe = re.sub(r'[^a-zA-Z0-9]+', '_', name)
    safe = safe.strip('_').lower()
    return f"{safe}.json" if safe else "uncategorized.json"

def parse_entries(data):
    categories = {}

    for e in data.get("entries", []):
        title = e.get("title")
        category = e.get("category", "Uncategorized")

        poster = None
        media_group = e.get("media_group", [])
        if media_group:
            imgs = media_group[0].get("media_item", [])
            if imgs:
                poster = imgs[-1]["src"]

        ext = e.get("extensions", {})
        start = (
            e.get("scheduled_start")
            or ext.get("VCH.ScheduledStart")
            or ext.get("match_date")
        )

        if not start and "actions" in ext:
            for act in ext.get("actions", []):
                if act.get("type") == "add_to_calendar":
                    ts = act.get("options", {}).get("startDate")
                    if ts:
                        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                        start = dt.isoformat()
                        break

        # Convert format ke +07:00
        if isinstance(start, str):
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                dt = dt.astimezone(timezone(timedelta(hours=7)))
                start = dt.isoformat()
            except Exception:
                pass

        # Cari link m3u8
        src = None
        for link in e.get("links", []):
            if link.get("type") == "application/vnd.apple.mpegurl":
                src = link.get("href")
                break

        media_id = e.get("id")

        match = {
            "title": title,
            "start": start,
            "status": ext.get("status", "TBC" if not start else "Scheduled"),
            "src": src or (f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8" if media_id else None),
            "poster": poster or (f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920" if media_id else None)
        }

        filename = sanitize_filename(category)
        categories.setdefault(filename, []).append(match)

    return categories

def main():
    try:
        data = fetch_schedule()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

    categorized = parse_entries(data)

    updated_files = []
    for filename, matches in categorized.items():
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        else:
            old_data = []

        if old_data == matches:
            continue

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(matches, f, ensure_ascii=False, indent=2)
        updated_files.append((filename, len(matches)))

    if updated_files:
        for fn, count in updated_files:
            print(f"📊 Update tersimpan ke {fn} ({count} pertandingan).")
    else:
        print("⚡ Tidak ada update dari web sumber → skip workflow.")

if __name__ == "__main__":
    main()
