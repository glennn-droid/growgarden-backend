# api/worker.py (Versi Final dengan Ingatan & Notifikasi Perubahan)
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, messaging
from .scraper import get_current_stock

# --- Inisialisasi Firebase ---
cred_json_str = os.environ.get('FIREBASE_CREDENTIALS')
if cred_json_str and not firebase_admin._apps:
    cred_dict = json.loads(cred_json_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()
# -----------------------------

def check_stock_and_notify():
    """
    Fungsi final:
    1. Ambil stok terbaru.
    2. Ambil stok lama dari database.
    3. Bandingkan, jika ada item BARU, baru kirim notifikasi.
    4. Simpan stok terbaru ke database untuk perbandingan berikutnya.
    """
    print("Mulai menjalankan pengecekan stok cerdas...")
    
    # 1. Ambil stok terbaru
    live_stock_list = get_current_stock()
    # Ubah ke Set untuk perbandingan. Kita hanya butuh namanya.
    current_stock_set = {item['name'] for item in live_stock_list}
    
    if not current_stock_set:
        print("Stok saat ini kosong.")
        return

    # 2. Ambil stok lama dari Firestore
    previous_stock_ref = db.collection('internal_state').document('last_stock')
    try:
        previous_stock_doc = previous_stock_ref.get()
        if previous_stock_doc.exists:
            previous_stock_set = set(previous_stock_doc.to_dict().get('items', []))
        else:
            previous_stock_set = set() # Jika belum ada data sebelumnya
    except Exception as e:
        print(f"Gagal mengambil stok lama dari Firestore: {e}")
        previous_stock_set = set()

    # 3. Bandingkan! Cari item yang BARU muncul
    newly_added_items = current_stock_set - previous_stock_set
    
    if not newly_added_items:
        print("Tidak ada item baru. Tidak ada notifikasi dikirim.")
        # Tetap simpan stok saat ini untuk menjaga data tetap update
        previous_stock_ref.set({'items': list(current_stock_set)})
        return
        
    print(f"Item BARU ditemukan: {newly_added_items}")

    # Ambil semua data device/wishlist dari Firestore
    devices_ref = db.collection('devices')
    all_devices = devices_ref.stream()

    # Looping setiap device untuk dicek
    for device in all_devices:
        device_data = device.to_dict()
        fcm_token = device.id
        wishlist = device_data.get('wishlist', [])
        if not wishlist: continue
        
        wishlist_set = set(wishlist)
        # Cari item yang cocok antara wishlist dan item BARU
        matched_items = newly_added_items.intersection(wishlist_set)

        if matched_items:
            item_names = ", ".join(list(matched_items))
            print(f"NOTIFIKASI UNTUK {fcm_token}: Item favorit BARU ada di stok! -> {item_names}")
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title='Item Favorit Baru Tersedia!',
                    body=f'Segera cek, ada {item_names} di toko!'
                ),
                token=fcm_token,
            )
            try:
                messaging.send(message)
                print(f'Notifikasi untuk {item_names} berhasil dikirim.')
            except Exception as e:
                print(f'Gagal mengirim notifikasi ke {fcm_token}: {e}')

    # 4. Simpan stok saat ini sebagai stok lama untuk pengecekan berikutnya
    print("Menyimpan stok saat ini ke database...")
    previous_stock_ref.set({'items': list(current_stock_set)})
    
    print("Pengecekan stok cerdas selesai.")