import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, messaging
from .scraper import get_current_stock # Jangan lupa titik di depan

# Mengambil kredensial dari Vercel Environment Variables
# Ini akan membaca 'secret' yang sudah kita setel di Vercel
cred_json_str = os.environ.get('FIREBASE_CREDENTIALS')

# Inisialisasi Firebase hanya jika kredensial ada
# dan jika belum pernah diinisialisasi sebelumnya
if cred_json_str and not firebase_admin._apps:
    cred_dict = json.loads(cred_json_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def check_stock_and_notify():
    """
    Fungsi utama yang akan dipanggil untuk mengecek stok dan mengirim notifikasi.
    """
    print("Mulai menjalankan pengecekan stok...")
    live_stock = get_current_stock()
    
    if not live_stock:
        print("Stok saat ini kosong. Tidak ada notifikasi dikirim.")
        return

    # Buat Set dari nama item untuk perbandingan yang efisien
    live_stock_set = {item['name'] for item in live_stock}
    print(f"Stok saat ini: {live_stock_set}")

    # Ambil semua data device/wishlist dari Firestore
    devices_ref = db.collection('devices')
    all_devices = devices_ref.stream()

    # Looping setiap device untuk dicek
    for device in all_devices:
        device_data = device.to_dict()
        fcm_token = device.id
        wishlist = device_data.get('wishlist', [])

        if not wishlist:
            continue

        wishlist_set = set(wishlist)
        # Cari item yang cocok antara wishlist dan live stock
        matched_items = live_stock_set.intersection(wishlist_set)

        if matched_items:
            item_names = ", ".join(list(matched_items))
            print(f"NOTIFIKASI UNTUK {fcm_token}: Item favoritmu ada yang stok! -> {item_names}")
            
            # Buat pesan notifikasi
            message = messaging.Message(
                notification=messaging.Notification(
                    title='Item Favoritmu Tersedia!',
                    body=f'Segera cek, ada {item_names} di toko!'
                ),
                token=fcm_token,
            )
            
            # Kirim notifikasi
            try:
                response = messaging.send(message)
                print('Notifikasi berhasil dikirim:', response)
            except Exception as e:
                print(f'Gagal mengirim notifikasi ke {fcm_token}: {e}')

    print("Pengecekan stok selesai.")