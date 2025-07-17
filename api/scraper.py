# api/scraper.py (Versi Investigasi)
import requests

def get_current_stock():
    """
    Mengambil data stok langsung dari API Supabase dengan penanganan error yang detail.
    """
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZleHRiemF0cHBybmtzeXV0YmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcxODQwODEsImV4cCI6MjA2Mjc2MDA4MX0.NKrxJnejTBezJ9R1uKE1B1bTp6Pgq5SMiqpAokCC_-o"

    headers = {
        'apikey': API_KEY,
        'Authorization': f'Bearer {API_KEY}'
    }

    urls = {
        "gear": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&type=eq.gear_stock&active=eq.true",
        "seeds": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&type=eq.seeds_stock&active=eq.true",
        "egg": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&type=eq.egg_stock&active=eq.true"
    }

    all_items_with_details = []

    for category, url in urls.items():
        try:
            print(f"Mengambil data untuk kategori: {category}...")
            response = requests.get(url, headers=headers)

            # --- BAGIAN DIAGNOSIS BARU ---
            if response.status_code == 200:
                items = response.json()
                for item_obj in items:
                    if item_obj.get("name"):
                        all_items_with_details.append({
                            "name": item_obj.get("name"),
                            "category": category
                        })
            else:
                # Jika status bukan 200 OK, cetak pesan error detail dari Supabase
                print(f"--- ERROR DETAIL UNTUK {category.upper()} ---")
                print(f"Status Code: {response.status_code}")
                print(f"Pesan dari Server: {response.text}")
                print("---------------------------------")
            # --- AKHIR BAGIAN DIAGNOSIS ---

        except Exception as e:
            print(f"Gagal total pada saat request untuk {category}: {e}")
            continue

    return all_items_with_details