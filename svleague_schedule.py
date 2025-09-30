import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_schedule(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    matches = []
    for match in soup.select(".match_card"):  # Sesuaikan dengan selector yang tepat
        title = match.select_one(".match_title").text.strip()
        date_str = match.select_one(".match_date").text.strip()
        time_str = match.select_one(".match_time").text.strip()
        start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        start_iso = start_time.isoformat()
        
        # Mencari URL siaran langsung dan poster
        src = match.select_one("a.live_stream")["href"] if match.select_one("a.live_stream") else ""
        poster = match.select_one("img.poster")["src"] if match.select_one("img.poster") else ""
        
        matches.append({
            "title": title,
            "start": start_iso,
            "src": src,
            "poster": poster
        })
    
    return matches

# URL untuk jadwal pria dan wanita
urls = {
    "men": "https://www.svleague.jp/en/sv_men/match/list",
    "women": "https://www.svleague.jp/en/sv_women/match/list"
}

# Mengambil jadwal untuk pria dan wanita
schedule = {}
for gender, url in urls.items():
    schedule[gender] = fetch_schedule(url)

# Menyimpan data ke file JSON
with open("svleague_schedule.json", "w", encoding="utf-8") as f:
    json.dump(schedule, f, ensure_ascii=False, indent=2)

print("✅ Jadwal pertandingan telah disimpan ke svleague_schedule.json")
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
