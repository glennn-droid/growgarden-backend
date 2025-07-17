import requests

def get_current_stock():
    """
    Mengambil data stok langsung dari API Supabase.
    """
    # Kunci API yang kamu temukan
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZleHRiemF0cHBybmtzeXV0YmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcxODQwODEsImV4cCI6MjA2Mjc2MDA4MX0.NKrxJnejTBezJ9R1uKE1B1bTp6Pgq5SMiqpAokCC_-o"
    
    headers = {
        'apikey': API_KEY,
        'Authorization': f'Bearer {API_KEY}'
    }

    urls = {
        "gear": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&type=eq.gear_stock&active=eq.true&order=created_at.desc",
        "seeds": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&type=eq.seeds_stock&active=eq.true&order=created_at.desc",
        "egg": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=name&type=eq.egg_stock&active=eq.true&order=created_at.desc"
    }

    all_items_with_details = []

    for category, url in urls.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            items = response.json()
            
            for item_obj in items:
                # Pastikan 'name' tidak None sebelum menambahkannya
                if item_obj.get("name"):
                    all_items_with_details.append({
                        "name": item_obj.get("name"),
                        "category": category
                    })

        except Exception as e:
            print(f"Gagal mengambil data untuk {category}: {e}")
            continue

    return all_items_with_details