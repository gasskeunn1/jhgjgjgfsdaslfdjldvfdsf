import requests, json
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

SCHEDULE_URL = "https://tv.volleyballworld.com/schedule"
PLAYLIST_URL = "https://zapp-5434-volleyball-tv.web.app/jw/playlists/FljcQiNy"
OUTFILE = "volleyballworld.json"

def fetch_playlist():
    r = requests.get(PLAYLIST_URL, timeout=20)
    r.raise_for_status()
    data = r.json()
    playlist = {}
    for e in data.get("entry", []):
        title = e.get("title")
        media_id = e.get("id")
        start = e.get("extensions", {}).get("VCH.ScheduledStart")
        if start:
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            dt = dt.astimezone(timezone(timedelta(hours=7)))
            start = dt.isoformat()
        playlist[title] = {
            "media_id": media_id,
            "start": start
        }
    return playlist

def fetch_schedule_website():
    r = requests.get(SCHEDULE_URL, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    matches = []

    for item in soup.select(".match-card"):
        title_tag = item.select_one(".match-card__title")
        time_tag = item.select_one(".match-card__time")
        if not title_tag or not time_tag:
            continue
        title = title_tag.get_text(strip=True)
        time_text = time_tag.get_text(strip=True)  # e.g., "Sel 07-10-2025 22:00 WIB"
        try:
            dt = datetime.strptime(time_text, "%a %d-%m-%Y %H:%M WIB")
            dt = dt.replace(tzinfo=timezone(timedelta(hours=7)))
            start = dt.isoformat()
        except:
            start = None
        matches.append({
            "title": title,
            "start": start
        })
    return matches

def combine_data(schedule, playlist):
    combined = []
    for match in schedule:
        title = match["title"]
        start_website = match["start"]
        media_info = playlist.get(title, {})
        media_id = media_info.get("media_id")
        start_playlist = media_info.get("start")
        final_start = start_playlist or start_website
        combined.append({
            "title": title,
            "start": final_start,
            "src": f"https://livecdn.euw1-0005.jwplive.com/live/sites/fM9jRrkn/media/{media_id}/live.isml/.m3u8" if media_id else None,
            "poster": f"https://cdn.jwplayer.com/v2/media/{media_id}/poster.jpg?width=1920" if media_id else None
        })
    return combined

def main():
    playlist = fetch_playlist()
    schedule = fetch_schedule_website()
    data = combine_data(schedule, playlist)

    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Jadwal lengkap tersimpan ({len(data)} pertandingan) ke {OUTFILE}")

if __name__ == "__main__":
    main()
