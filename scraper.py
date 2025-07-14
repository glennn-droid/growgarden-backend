# scraper.py (Versi 2.1 - dengan kategori)

import requests
import time
from item_database import ALL_POSSIBLE_ITEMS # Import kamus kita

GEAR_SEEDS_URL = "https://growagardenstock.com/api/stock?type=gear-seeds"
EGG_URL = "https://growagardenstock.com/api/stock?type=egg"

# Membuat sebuah "peta balik" untuk mencari kategori dari nama item dengan cepat
ITEM_TO_CATEGORY_MAP = {}
for category, items in ALL_POSSIBLE_ITEMS.items():
    for item in items:
        ITEM_TO_CATEGORY_MAP[item] = category

def get_current_stock():
    """
    Mengambil data stok dari API dan menyertakan kategori untuk setiap item.
    Sekarang akan mengembalikan list of dictionaries, contoh:
    [{"name": "Carrot", "category": "seeds"}, {"name": "Trowel", "category": "gear"}]
    """
    all_items_with_details = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        timestamp = int(time.time() * 1000)
        
        # --- Ambil data Gear & Seeds ---
        response_gs = requests.get(f"{GEAR_SEEDS_URL}&ts={timestamp}", headers=headers)
        response_gs.raise_for_status()
        data_gs = response_gs.json()

        raw_items = []
        if 'gear' in data_gs:
            raw_items.extend(data_gs['gear'])
        if 'seeds' in data_gs:
            raw_items.extend(data_gs['seeds'])

        # --- Ambil data Egg ---
        response_egg = requests.get(f"{EGG_URL}&ts={timestamp}", headers=headers)
        response_egg.raise_for_status()
        data_egg = response_egg.json()

        if 'egg' in data_egg:
            raw_items.extend(data_egg['egg'])
            
        # --- Proses dan tambahkan kategori ---
        for raw_item_string in raw_items:
            # Membersihkan nama item dari teks jumlah (misal, '**x16**')
            clean_name = raw_item_string.split('**')[0].strip()
            # Cari kategori item dari peta yang kita buat
            category = ITEM_TO_CATEGORY_MAP.get(clean_name, "unknown") # Default 'unknown' jika tidak ada di kamus
            
            all_items_with_details.append({
                "name": clean_name,
                "category": category
            })

        return all_items_with_details

    except Exception as e:
        print(f"Terjadi error di scraper: {e}")
        return []

if __name__ == "__main__":
    print("Mencoba mengambil stok dengan detail kategori...")
    current_stock = get_current_stock()
    
    if current_stock:
        print("Berhasil! Item yang sedang stock:")
        print(current_stock)
    else:
        print("Gagal mendapatkan stok atau stok memang kosong.")