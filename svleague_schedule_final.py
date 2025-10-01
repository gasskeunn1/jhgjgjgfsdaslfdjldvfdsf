import requests
import json
from datetime import datetime

def fetch_schedule(url, gender, tz="+09:00"):
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    matches = []
    for match in data.get("list", []):
        try:
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            title = f"{home} v {away}"

            # start time
            start_raw = match["matchDate"] + " " + match["matchTime"]
            start_iso = datetime.strptime(start_raw, "%Y/%m/%d %H:%M").strftime("%Y-%m-%dT%H:%M:00") + tz

            # link & poster
            src = f"https://www.svleague.jp/en/{gender}/match/detail/{match['id']}"
            poster = match.get("image", "")

            matches.append({
                "title": title,
                "start": start_iso,
                "src": src,
                "poster": poster
            })
        except Exception as e:
            print("⚠️ error parse:", e)
            continue

    return matches

schedule = {
    "men": fetch_schedule("https://www.svleague.jp/en/sv_men/match/list?season=2025", "sv_men"),
    "women": fetch_schedule("https://www.svleague.jp/en/sv_women/match/list?season=2025", "sv_women")
}

with open("svleague_schedule.json", "w", encoding="utf-8") as f:
    json.dump(schedule, f, ensure_ascii=False, indent=2)

print("✅ Jadwal pria & wanita berhasil disimpan ke svleague_schedule.json")
