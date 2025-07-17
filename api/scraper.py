# api/scraper.py (Versi Final dengan Perbaikan Format Waktu)
import requests
from datetime import datetime, timedelta, timezone

def get_current_stock():
    """
    Mengambil data stok langsung dari API Supabase dengan filter waktu yang benar.
    """
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZleHRiemF0cHBybmtzeXV0YmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcxODQwODEsImV4cCI6MjA2Mjc2MDA4MX0.NKrxJnejTBezJ9R1uKE1B1bTp6Pgq5SMiqpAokCC_-o"
    
    headers = {
        'apikey': API_KEY,
        'Authorization': f'Bearer {API_KEY}'
    }

    # --- PERBAIKAN DI SINI ---
    # Membuat filter waktu: ambil data dari 10 menit terakhir
    # Format diubah agar sesuai dengan yang diinginkan Supabase (diakhiri dengan 'Z')
    time_filter_dt = datetime.now(timezone.utc) - timedelta(minutes=10)
    time_filter = time_filter_dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    # -------------------------

    base_url = "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&active=eq.true&order=created_at.desc"
    
    urls = {
        "gear": f"{base_url}&type=eq.gear_stock&created_at=gte.{time_filter}",
        "seeds": f"{base_url}&type=eq.seeds_stock&created_at=gte.{time_filter}",
        "egg": f"{base_url}&type=eq.egg_stock&created_at=gte.{time_filter}"
    }

    all_items_with_details = []

    for category, url in urls.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
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