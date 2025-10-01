import requests, json, os, sys
from datetime import datetime, timezone, timedelta

URL = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/8PkxmOMj"
INDOOR_FILE = "indoor_live.json"
BEACH_FILE = "beach_live.json"

def fetch_schedule():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()
    data = r.json()
    return data.get("entry", [])

def parse_entries(entries):
    indoor = []
    beach = []

    for e in entries:
        title = e.get("title")
        comp_type = e.get("extensions", {}).get("tags", "").lower()  # gunakan tags untuk menentukan jenis
        media_group = e.get("media_group", [])
        poster = None
        if media_group:
            imgs = media_group[0].get("media_item", [])
            if imgs:
                poster = imgs[-1]["src"]

        playlists = e.get("hubPlaylists", {})
        playlist_links = [f"https://zapp-5434-volleyball-tv.web.app/jw/playlists/{pid}" for pid in playlists.values()]

        entry_data = {
            "title": title,
            "poster": poster,
            "playlists": playlist_links
        }

        if "beach" in comp_type:
            beach.append(entry_data)
        else:
            indoor.append(entry_data)

    return indoor, beach

def save_file(filename, data):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    else:
        old_data = []

    if old_data == data:
        print(f"⚡ Tidak ada update → skip {filename}.")
        return False

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📊 Update tersimpan di {filename} ({len(data)} jadwal).")
    return True

def main():
    try:
        entries = fetch_schedule()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

    indoor, beach = parse_entries(entries)

    updated_indoor = save_file(INDOOR_FILE, indoor)
    updated_beach = save_file(BEACH_FILE, beach)

    if updated_indoor or updated_beach:
        print("✅ Ada update → siap untuk push.")
    else:
        print("⚡ Tidak ada update → skip push.")

if __name__ == "__main__":
    main()
