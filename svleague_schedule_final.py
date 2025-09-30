from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json
import re

def fetch_schedule_final(url, season_year="2025", tz="+09:00"):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(url)
    driver.implicitly_wait(10)

    matches = []
    match_elements = driver.find_elements(By.CSS_SELECTOR, ".match-card")

    for match in match_elements:
        try:
            title = match.find_element(By.CSS_SELECTOR, ".match-title").text.strip()
            date_time_text = match.find_element(By.CSS_SELECTOR, ".match-date").text.strip()
            parts = date_time_text.replace("(", "").replace(")", "").split()
            date_part, time_part = parts[1], parts[2]
            date_str = date_part.replace(".", "-")
            start_iso = f"{season_year}-{date_str}T{time_part}:00{tz}"

            # Link detail pertandingan
            src_tag = match.find_element(By.CSS_SELECTOR, "a")
            detail_url = src_tag.get_attribute("href") if src_tag else ""

            # Poster resmi (cepat)
            match_id = detail_url.split("/")[-1] if detail_url else "default"
            poster = f"https://www.svleague.jp/en/sv_women/match/img/{match_id}.jpg" if "women" in url else f"https://www.svleague.jp/en/sv_men/match/img/{match_id}.jpg"

            # Streaming .m3u8 (jika ada)
            # Cek data-live-src atau pattern di halaman
            m3u8 = ""
            try:
                live_tag = match.find_elements(By.CSS_SELECTOR, "a[data-live-src]")
                if live_tag:
                    m3u8 = live_tag[0].get_attribute("data-live-src")
            except:
                m3u8 = ""

            matches.append({
                "title": title,
                "start": start_iso,
                "src": m3u8 if m3u8 else detail_url,
                "poster": poster
            })
        except Exception as e:
            print("⚠️ Error parsing match:", e)
            continue

    driver.quit()
    return matches

# URLs jadwal pria & wanita
urls = {
    "men": "https://www.svleague.jp/en/sv_men/match/list",
    "women": "https://www.svleague.jp/en/sv_women/match/list"
}

schedule = {}
for gender, url in urls.items():
    print(f"Fetching schedule for {gender}...")
    schedule[gender] = fetch_schedule_final(url)

# Simpan JSON final
with open("svleague_schedule.json", "w", encoding="utf-8") as f:
    json.dump(schedule, f, ensure_ascii=False, indent=2)

print("✅ Jadwal pria & wanita dengan poster dan link streaming .m3u8 berhasil disimpan ke svleague_schedule.json")
