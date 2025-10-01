import requests, json, os, sys
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

URL = "https://tv.volleyballworld.com/schedule"
OUTDIR = "schedules"

def fetch_schedule():
    r = requests.get(URL, timeout=30)
    r.raise_for_status()
    return r.text

def parse_schedule(html):
    soup = BeautifulSoup(html, "html.parser")
    categories = {}

    # ambil blok kategori
    for block in soup.select("section[class*='Category']"):
        category = block.find("h2")
        if not category:
            continue
        cat_name = category.get_text(strip=True)
        cat_key = cat_name.lower().replace(" ", "_")

        matches = []
        for match in block.select("article"):
            title = match.get_text(" ", strip=True)

            # ambil waktu
            time_tag = match.find("time")
            start = None
            if time_tag and time_tag.has_attr("datetime"):
                try:
                    dt = datetime.fromisoformat(time_tag["datetime"].replace("Z", "+00:00"))
                    dt = dt.astimezone(timezone(timedelta(hours=7)))
                    start = dt.isoformat()
                except Exception:
                    start = time_tag["datetime"]

            # poster (jika ada)
            img = match.find("img")
            poster = img["src"] if img and img.has_attr("src") else None

            matches.append({
                "title": title,
                "start": start,
                "poster": poster
            })

        categories[cat_key] = {
            "category": cat_name,
            "matches": matches
        }

    return categories

def save_categories(categories):
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)

    # hapus file lama yang kategorinya sudah tidak ada
    old_files = {f for f in os.listdir(OUTDIR) if f.endswith(".json")}
    new_files = set()

    for cat_key, data in categories.items():
        outfile = f"{cat_key}.json"
        new_files.add(outfile)
        path = os.path.join(OUTDIR, outfile)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"📁 {outfile} tersimpan ({len(data['matches'])} pertandingan).")

    # hapus file lama yang sudah tidak ada di kategori baru
    for old in old_files - new_files:
        os.remove(os.path.join(OUTDIR, old))
        print(f"🗑️ {old} dihapus (tidak ada di web sumber).")

def main():
    try:
        html = fetch_schedule()
    except Exception as e:
        print("❌ Gagal fetch data:", e)
        sys.exit(1)

    categories = parse_schedule(html)
    if not categories:
        print("⚡ Tidak ada kategori ditemukan di web sumber.")
        sys.exit(0)

    save_categories(categories)

if __name__ == "__main__":
    main()
