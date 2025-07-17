# api/worker.py (Versi Final - Logika Hibrida)
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, messaging
from .scraper import get_current_stock_grouped # Pastikan import fungsi yang benar

# --- Inisialisasi Firebase ---
cred_json_str = os.environ.get('FIREBASE_CREDENTIALS')
if cred_json_str and not firebase_admin._apps:
    cred_dict = json.loads(cred_json_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()
# -----------------------------

def process_category_with_memory(category_name, current_items_set, all_devices_wishlists):
    """
    Fungsi cerdas untuk SEEDS dan GEAR.
    Hanya mengirim notifikasi jika stok berubah.
    """
    previous_stock_ref = db.collection('internal_state').document(f'last_stock_{category_name}')
    try:
        previous_stock_doc = previous_stock_ref.get()
        previous_stock_set = set(previous_stock_doc.to_dict().get('items', [])) if previous_stock_doc.exists else set()
    except Exception:
        previous_stock_set = set()

    # Hanya proses jika stok untuk kategori ini berubah
    if current_items_set == previous_stock_set:
        print(f"Stok untuk '{category_name}' tidak berubah.")
        return

    print(f"Stok untuk '{category_name}' berubah! Stok baru: {current_items_set}")
    
    # Kirim notifikasi ke user yang relevan
    for fcm_token, wishlist_set in all_devices_wishlists.items():
        matched_items = current_items_set.intersection(wishlist_set)
        if matched_items:
            item_names = ", ".join(list(matched_items))
            print(f"NOTIFIKASI {category_name.upper()} UNTUK {fcm_token}: {item_names}")
            message = messaging.Message(
                notification=messaging.Notification(title=f'Stok {category_name.capitalize()} Baru!', body=f'Ada {item_names} di toko!'),
                token=fcm_token,
            )
            try:
                messaging.send(message)
            except Exception as e:
                print(f'Gagal mengirim notifikasi ke {fcm_token}: {e}')

    # Update ingatan untuk kategori ini
    previous_stock_ref.set({'items': list(current_items_set)})

def process_category_direct(category_name, current_items_set, all_devices_wishlists):
    """
    Fungsi simpel untuk EGG.
    Selalu mengirim notifikasi jika ada item di wishlist.
    """
    print(f"Mengecek stok '{category_name}' secara langsung. Stok saat ini: {current_items_set}")
    
    # Langsung kirim notifikasi ke user yang relevan tanpa cek ingatan
    for fcm_token, wishlist_set in all_devices_wishlists.items():
        matched_items = current_items_set.intersection(wishlist_set)
        if matched_items:
            item_names = ", ".join(list(matched_items))
            print(f"NOTIFIKASI {category_name.upper()} UNTUK {fcm_token}: {item_names}")
            message = messaging.Message(
                notification=messaging.Notification(title=f'Stok {category_name.capitalize()} Tersedia!', body=f'Ada {item_names} di toko!'),
                token=fcm_token,
            )
            try:
                messaging.send(message)
            except Exception as e:
                print(f'Gagal mengirim notifikasi ke {fcm_token}: {e}')

def check_stock_and_notify():
    print("\n--- Memulai Pengecekan Stok Hibrida ---")
    
    # 1. Ambil semua stok, sudah dikelompokkan
    grouped_stock = get_current_stock_grouped()
    if not any(grouped_stock.values()):
        print("Semua stok kosong.")
        return

    # 2. Ambil semua wishlist dari semua user SEKALI SAJA
    all_devices_wishlists = {}
    devices_ref = db.collection('devices')
    all_devices = devices_ref.stream()
    for device in all_devices:
        all_devices_wishlists[device.id] = set(device.to_dict().get('wishlist', []))

    # 3. Proses setiap kategori dengan logika yang berbeda
    # Gunakan logika "ingatan" untuk seeds dan gear
    process_category_with_memory('seeds', set(grouped_stock.get('seeds', [])), all_devices_wishlists)
    process_category_with_memory('gear', set(grouped_stock.get('gear', [])), all_devices_wishlists)
    
    # Gunakan logika "langsung" untuk egg
    process_category_direct('egg', set(grouped_stock.get('egg', [])), all_devices_wishlists)

    print("--- Pengecekan Stok Hibrida Selesai ---\n")
