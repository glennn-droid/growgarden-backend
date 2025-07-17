# api/scraper.py (Versi Investigasi Final)
import requests

def get_current_stock():
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZleHRiemF0cHBybmtzeXV0YmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcxODQwODEsImV4cCI6MjA2Mjc2MDA4MX0.NKrxJnejTBezJ9R1uKE1B1bTp6Pgq5SMiqpAokCC_-o"
    headers = {'apikey': API_KEY, 'Authorization': f'Bearer {API_KEY}'}

    # Mengubah select=name menjadi select=* untuk melihat semua kolom
    urls = {
        "gear": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=*&type=eq.gear_stock&active=eq.true",
        "seeds": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=*&type=eq.seeds_stock&active=eq.true",
        "egg": "https://vextbzatpprnksyutbcp.supabase.co/rest/v1/growagarden_stock?select=*&type=eq.egg_stock&active=eq.true"
    }

    all_items_with_details = []
    for category, url in urls.items():
        try:
            print(f"Mengambil semua data untuk kategori: {category}...")
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                # Cetak data mentah yang kita terima
                print(f"--- DATA MENTAH UNTUK {category.upper()} ---")
                print(response.json())
                print("-----------------------------------")
                # Untuk sementara, kita tidak proses datanya dulu
                # Kita hanya ingin melihat strukturnya di log
            else:
                print(f"Error untuk {category}. Status: {response.status_code}. Pesan: {response.text}")
        except Exception as e:
            print(f"Gagal total pada saat request untuk {category}: {e}")

    # Fungsi ini akan mengembalikan list kosong, ini normal untuk tes ini
    return all_items_with_details