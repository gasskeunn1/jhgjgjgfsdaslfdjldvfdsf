import json
import requests

# URL JSON web source (contoh: endpoint yang explore_vbworld.py gunakan)
URL = "https://www.volleyballworld.com/api/homepage"  # ganti sesuai endpoint terbaru

# Fetch data dari web
response = requests.get(URL)
data = response.json()

# Fungsi ekstrak feed menjadi list pertandingan
def extract_feed(feed):
    matches = []
    for entry in feed.get("entry", []):
        match = {}
        match["title"] = entry.get("title") or entry.get("extensions", {}).get("actions", [{}])[0].get("options", {}).get("title")
        match["src"] = entry.get("extensions", {}).get("actions", [{}])[0].get("options", {}).get("url", None)
        match["start"] = entry.get("extensions", {}).get("actions", [{}])[0].get("options", {}).get("startTime", None)
        matches.append(match)
    return matches

# Indoor feed → serverLoadedFeeds[1]
indoor_feed = data["serverLoadedFeeds"][1]["feed"]
indoor_matches = extract_feed(indoor_feed)

# Beach feed → serverLoadedFeeds[2]
beach_feed = data["serverLoadedFeeds"][2]["feed"]
beach_matches = extract_feed(beach_feed)

# Simpan ke file JSON
with open("indoor_live.json", "w", encoding="utf-8") as f:
    json.dump(indoor_matches, f, ensure_ascii=False, indent=4)

with open("beach_live.json", "w", encoding="utf-8") as f:
    json.dump(beach_matches, f, ensure_ascii=False, indent=4)

print("✅ indoor_live.json & beach_live.json berhasil dibuat!")
