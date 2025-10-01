import requests, json, os, sys
from datetime import datetime, timezone, timedelta

URL = "https://tv.volleyballworld.com/?_data=routes%2F_index"
INDOOR_FILE = "indoor_live.json"
BEACH_FILE = "beach_live.json"

def fetch_schedule():
    try:
        r = requests.get(URL, timeout=20)
        r.raise_for_status()
        data = r.json()
        # Data biasanya ada di pageProps.liveEvents atau pageProps.initialState.matches
        events = data.get("pageProps", {}).get("liveEvents", [])
        if not events:
            events = data.get("pageProps", {}).get("initialState", {}).get("matches", [])
        return events
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

def parse_entries(entries, discipline_filter):
    result = []
    for e in entries:
        # Filter berdasarkan discipline
        discipline = e.get("discipline")
        if discipline_filter == "indoor" and discipline != "INDOOR":
            continue
        if discipline_filter == "beach" and discipline != "BEACH":
            continue

        title = e.get("homeTeam", {}).get("name") + " - " + e.get("awayTeam", {}).get("name") \
                if e.get("homeTeam") and e.get("awayTeam") else e.get("title", "Match")

        start = e.get("scheduledStart") or e.get("matchDate")
        if start:
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                dt = dt.astimezone(timezone(timedelta(hours=7)))
                start = dt.isoformat()
            except Exception:
                pass

        src = e.get("streamUrl")  # kadang ada, kadang tidak
        media_id = e.get("id")
        if not src and media_id:
            src = f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8"

        poster = e.get("poster") or f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920" if media_id else None

        result.append({
            "title": title,
            "start": start,
            "src": src,
            "poster": poster
        })
    return result

def save_if_changed(data, outfile):
    if os.path.exists(outfile):
        with open(outfile, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = []

    if old_data == data:
        print(f"⚡ Tidak ada update → skip {outfile}.")
        return False

    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📊 Update tersimpan di {outfile} ({len(data)} jadwal).")
    return True

def main():
    entries = fetch_schedule()
    indoor = parse_entries(entries, "indoor")
    beach = parse_entries(entries, "beach")

    save_if_changed(indoor, INDOOR_FILE)
    save_if_changed(beach, BEACH_FILE)

if __name__ == "__main__":
    main()
