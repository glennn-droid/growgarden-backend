# worker.py

import firebase_admin
from firebase_admin import credentials, firestore, messaging
from scraper import get_current_stock

# --- Setup Awal ---
# Inisialisasi Firebase (sama seperti di main.py)
cred = credentials.Certificate("firebase-credentials.json")
# Cek apakah aplikasi sudah diinisialisasi untuk menghindari error
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Dapatkan akses ke database Firestore
db = firestore.client()
# --------------------


def check_stock_and_notify():
    """
    Fungsi utama si penjaga.
    1. Ambil stok terbaru.
    2. Ambil semua wishlist dari database.
    3. Bandingkan, dan kirim notifikasi jika cocok.
    """
    print("Mulai menjalankan pengecekan stok...")

    # 1. Ambil stok terbaru dari scraper kita
    live_stock = get_current_stock()
    
    # Jika stok ternyata kosong, tidak ada yang perlu dilakukan
    if not live_stock:
        print("Stok saat ini kosong. Tidak ada notifikasi dikirim.")
        return

    print(f"Stok saat ini: {live_stock}")
    
    # Ubah list menjadi Set untuk perbandingan yang lebih cepat
    live_stock_set = set(live_stock)

    # 2. Ambil semua data device/wishlist dari Firestore
    devices_ref = db.collection('devices')
    all_devices = devices_ref.stream()

    # 3. Looping setiap device untuk dicek
    for device in all_devices:
        device_data = device.to_dict()
        fcm_token = device.id
        wishlist = device_data.get('wishlist', [])

        if not wishlist:
            continue # Lanjut ke device berikutnya jika wishlist kosong

        # Bandingkan wishlist dengan stok yang ada
        wishlist_set = set(wishlist)
        matched_items = live_stock_set.intersection(wishlist_set)

        # Jika ada item yang cocok...
        if matched_items:
            # Ubah Set kembali menjadi list string
            matched_items_list = list(matched_items)
            
            # Buat pesan notifikasi
            item_names = ", ".join(matched_items_list)
            print(f"NOTIFIKASI UNTUK {fcm_token}: Item favoritmu ada yang stok! -> {item_names}")
            
            # Kirim notifikasi menggunakan FCM
            message = messaging.Message(
                notification=messaging.Notification(
                    title='Item Favoritmu Tersedia!',
                    body=f'Segera cek, ada {item_names} di toko!'
                ),
                token=fcm_token,
            )
            
            try:
                response = messaging.send(message)
                print('Notifikasi berhasil dikirim:', response)
            except Exception as e:
                print(f'Gagal mengirim notifikasi ke {fcm_token}: {e}')

    print("Pengecekan stok selesai.")


# --- Bagian untuk menjalankan fungsi ini secara langsung untuk tes ---
if __name__ == "__main__":
    check_stock_and_notify()