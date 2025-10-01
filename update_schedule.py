import requests, json, os
from datetime import datetime, timezone, timedelta

BASE = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/"
GROUPS_URL = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/0seCz8gr"
OUTDIR = "schedules"

def fetch_json(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()

def fetch_group_playlists():
    data = fetch_json(GROUPS_URL)
    return [e for e in data.get("entry", []) if e.get("type", {}).get("value") == "competition_group"]

def fetch_schedule(playlist_id):
    try:
        data = fetch_json(BASE + playlist_id)
        return data.get("entry", [])
    except Exception as e:
        print(f"❌ Gagal fetch playlist {playlist_id}: {e}")
        return []

def parse_entries(entries):
    result = []
    for e in entries:
        ext = e.get("extensions", {})
        status = (e.get("status") or ext.get("status") or "").lower()
        if status not in ("live", "upcoming", "scheduled"):
            continue

        title = e.get("title")

        # poster
        poster = None
        media_group = e.get("media_group", [])
        if media_group:
            imgs = media_group[0].get("media_item", [])
            if imgs:
                poster = imgs[-1]["src"]

        # start
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
                dt = dt.astimezone(timezone(timedelta(hours=7)))  # WIB +7
                start = dt.isoformat()
            except Exception:
                pass

        # src
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

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📊 Update tersimpan ke {path} ({len(data)} jadwal).")

def main():
    groups = fetch_group_playlists()
    indoor_data, beach_data = [], []

    for g in groups:
        code = (g.get("extensions", {}).get("competition_group_code") or "").lower()
        title_group = (g.get("title") or "").lower()
        playlists = g.get("extensions", {}).get("hubPlaylists", {})
        ids = [v for v in playlists.values()]

        all_entries = []
        for pid in ids:
            all_entries.extend(fetch_schedule(pid))

        parsed = parse_entries(all_entries)

        # Tentukan Indoor / Beach berdasarkan code atau title
        if "beach" in code or "beach" in title_group:
            beach_data.extend(parsed)
        else:
            indoor_data.extend(parsed)

    save_json(os.path.join(OUTDIR, "indoor_live.json"), indoor_data)
    save_json(os.path.join(OUTDIR, "beach_live.json"), beach_data)

if __name__ == "__main__":
    main()
