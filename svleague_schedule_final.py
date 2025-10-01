from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json

def fetch_schedule(url, season_year="2025", tz="+09:00"):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(url)
    wait = WebDriverWait(driver, 20)

    # Tunggu semua pertandingan muncul (sesuaikan selector terbaru)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/match/detail/']")))

    matches = []
    # Ambil semua link detail
    detail_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/match/detail/']")

    for link in detail_links:
        try:
            src = link.get_attribute("href")
            parent = link.find_element(By.XPATH, "./..")  # parent container
            # Ambil tim home & away
            home_team = parent.find_element(By.CSS_SELECTOR, ".team-home").text.strip()
            away_team = parent.find_element(By.CSS_SELECTOR, ".team-away").text.strip()
            title = f"{home_team} v {away_team}"

            # Ambil tanggal & waktu
            date_time_text = parent.find_element(By.CSS_SELECTOR, ".match-date").text.strip()
            parts = date_time_text.replace("(", "").replace(")", "").split()
            date_part, time_part = parts[1], parts[2]
            date_str = date_part.replace(".", "-")
            start_iso = f"{season_year}-{date_str}T{time_part}:00{tz}"

            # Poster cepat dari match_id
            match_id = src.split("/")[-1]
            poster = f"https://www.svleague.jp/en/sv_men/match/img/{match_id}.jpg" if "men" in url else f"https://www.svleague.jp/en/sv_women/match/img/{match_id}.jpg"

            matches.append({
                "title": title,
                "start": start_iso,
                "src": src,
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
    schedule[gender] = fetch_schedule(url)

# Simpan JSON
with open("svleague_schedule.json", "w", encoding="utf-8") as f:
    json.dump(schedule, f, ensure_ascii=False, indent=2)

print("✅ Jadwal pria & wanita berhasil disimpan ke svleague_schedule.json")
