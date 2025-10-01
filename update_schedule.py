import requests, json, os, sys
from datetime import datetime, timezone, timedelta

OUTDIR = "schedules"
INDOOR_FILE = os.path.join(OUTDIR, "indoor.json")
BEACH_FILE = os.path.join(OUTDIR, "beach.json")

URL_INDOOR = "https://tv.volleyballworld.com/schedule"
URL_BEACH = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/FljcQiNy"


def convert_time(ts: str | None):
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        dt = dt.astimezone(timezone(timedelta(hours=7)))
        return dt.isoformat()
    except Exception:
        return ts


def fetch_indoor():
    try:
        r = requests.get(URL_INDOOR, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("❌ Gagal fetch indoor:", e)
        return []

    result = []
    events = data.get("events", [])
    for e in events:
        result.append({
            "title": e.get("title"),
            "start": convert_time(e.get("startDate")),
            "poster": e.get("image", {}).get("src"),
            "src": None,  # indoor tidak ada langsung .m3u8
            "category": e.get("category", {}).get("name")
        })
    return result


def fetch_beach():
    try:
        r = requests.get(URL_BEACH, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("❌ Gagal fetch beach:", e)
        return []

    result = []
    for e in data.get("entry", []):
        title = e.get("title")
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

        start = convert_time(start)
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
            "poster": poster or f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920"
        })
    return result


def save_if_changed(path, new_data):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = []

    if old_data == new_data:
        print(f"⚡ Tidak ada update untuk {path}")
        return False

    with open(path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"📊 Update tersimpan ke {path} ({len(new_data)} jadwal).")
    return True


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    changed = False
    indoor_data = fetch_indoor()
    beach_data = fetch_beach()

    if save_if_changed(INDOOR_FILE, indoor_data):
        changed = True
    if save_if_changed(BEACH_FILE, beach_data):
        changed = True

    if not changed:
        sys.exit(0)


if __name__ == "__main__":
    main()
