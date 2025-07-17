# api/scraper.py (Versi Final Sebenarnya)
import requests

def get_current_stock():
    """
    Mengambil data stok langsung dari 3 endpoint API Supabase yang berbeda.
    """
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZleHRiemF0cHBybmtzeXV0YmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcxODQwODEsImV4cCI6MjA2Mjc2MDA4MX0.NKrxJnejTBezJ9R1uKE1B1bTp6Pgq5SMiqpAokCC_-o"

    headers = {
        'apikey': API_KEY,
        'Authorization': f'Bearer {API_KEY}'
    }

    # Kita gunakan 3 URL terpisah yang sudah terbukti benar
    urls = {
        "gear": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&type=eq.gear_stock&active=eq.true",
        "seeds": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&type=eq.seeds_stock&active=eq.true",
        "egg": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&type=eq.egg_stock&active=eq.true"
    }

    all_items_with_details = []

    # Looping untuk setiap kategori
    for category, url in urls.items():
        try:
            print(f"Mengambil data untuk kategori: {category}...")
            response = requests.get(url, headers=headers)
            response.raise_for_status() # Ini akan error jika status bukan 200
            items = response.json()

            for item_obj in items:
                if item_obj.get("name"):
                    all_items_with_details.append({
                        "name": item_obj.get("name"),
                        "category": category
                    })

        except Exception as e:
            print(f"Gagal mengambil data untuk {category}: {e}")
            continue

    return all_items_with_details