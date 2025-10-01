import requests, json, os, sys
from datetime import datetime, timezone, timedelta

URL = "https://tv.volleyballworld.com/?_data=routes%2F_index"
INDOOR_OUT = "indoor_live.json"
BEACH_OUT = "beach_live.json"

def fetch_schedule():
    try:
        r = requests.get(URL, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

def parse_schedule(data):
    indoor = []
    beach = []

    matches = data.get("props", {}).get("pageProps", {}).get("matches", [])
    for m in matches:
        title = m.get("title")
        start = m.get("startDateTime")  # biasanya ISO string
        comp_type = m.get("tournament", {}).get("discipline")  # "INDOOR" atau "BEACH"

        # convert ke WIB
        if start:
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                dt = dt.astimezone(timezone(timedelta(hours=7)))
                start = dt.isoformat()
            except Exception:
                pass

        # src / live url
        media_id = m.get("id")
        src = f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8"
        poster = f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920"

        item = {
            "title": title,
            "start": start,
            "src": src,
            "poster": poster
        }

        if comp_type == "BEACH":
            beach.append(item)
        else:
            indoor.append(item)

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
    data = fetch_schedule()
    indoor, beach = parse_schedule(data)

    changed_indoor = save_if_changed(INDOOR_OUT, indoor)
    changed_beach = save_if_changed(BEACH_OUT, beach)

    if not changed_indoor and not changed_beach:
        sys.exit(0)

if __name__ == "__main__":
    main()
