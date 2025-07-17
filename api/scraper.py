# api/scraper.py (Pastikan versinya seperti ini)
import requests

def get_current_stock():
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZleHRiemF0cHBybmtzeXV0YmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcxODQwODEsImV4cCI6MjA2Mjc2MDA4MX0.NKrxJnejTBezJ9R1uKE1B1bTp6Pgq5SMiqpAokCC_-o"
    headers = {'apikey': API_KEY, 'Authorization': f'Bearer {API_KEY}'}
    urls = {
        "gear": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=display_name&type=eq.gear_stock&active=eq.true",
        "seeds": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=display_name&type=eq.seeds_stock&active=eq.true",
        "egg": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=display_name&type=eq.egg_stock&active=eq.true"
    }
    all_items_with_details = []
    for category, url in urls.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            items = response.json()
            for item_obj in items:
                item_name = item_obj.get("display_name")
                if item_name:
                    all_items_with_details.append({"name": item_name, "category": category})
        except Exception as e:
            print(f"Gagal mengambil data untuk {category}: {e}")
    return all_items_with_details