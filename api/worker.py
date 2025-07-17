# api/worker.py (Versi Definitif - Pengingat Cerdas)
import os
import json
from datetime import datetime, timedelta, timezone
import firebase_admin
from firebase_admin import credentials, firestore, messaging
from .scraper import get_current_stock # Kita pakai scraper simpel lagi

# --- Inisialisasi Firebase ---
cred_json_str = os.environ.get('FIREBASE_CREDENTIALS')
if cred_json_str and not firebase_admin._apps:
    cred_dict = json.loads(cred_json_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()
# -----------------------------

def send_notification(fcm_token, item_name):
    """Fungsi terpisah untuk mengirim notifikasi."""
    print(f"MENGIRIM NOTIFIKASI untuk '{item_name}' ke token {fcm_token[:10]}...")
    message = messaging.Message(
        notification=messaging.Notification(
            title='Item Favoritmu di Toko!',
            body=f'Segera cek, {item_name} sedang tersedia!'
        ),
        token=fcm_token,
    )
    try:
        messaging.send(message)
        print(f"Notifikasi untuk '{item_name}' berhasil dikirim.")
        return True
    except Exception as e:
        print(f'Gagal mengirim notifikasi ke {fcm_token}: {e}')
        return False

def check_stock_and_notify():
    print("\n--- Memulai Pengecekan Stok dengan Pengingat Cerdas ---")
    
    # 1. Ambil stok terbaru
    live_stock_list = get_current_stock()
    if not live_stock_list:
        print("Stok saat ini kosong.")
        return

    # Buat dictionary untuk akses cepat: {'Carrot': 'seeds', 'Trowel': 'gear'}
    current_stock_map = {item['name']: item['category'] for item in live_stock_list}
    print(f"Stok saat ini: {list(current_stock_map.keys())}")

    # 2. Ambil semua data pengguna dari Firestore
    devices_ref = db.collection('devices')
    all_devices = devices_ref.stream()

    # 3. Looping setiap pengguna/perangkat
    for device in all_devices:
        device_data = device.to_dict()
        fcm_token = device.id
        wishlist = set(device_data.get('wishlist', []))
        # Ambil catatan waktu notifikasi terakhir, atau buat baru jika tidak ada
        last_notified_map = device_data.get('last_notified', {})
        
        if not wishlist:
            continue

        # Variabel untuk menandai apakah ada perubahan di catatan waktu
        did_update_timestamps = False

        # 4. Looping setiap item di wishlist pengguna
        for item_name in wishlist:
            # Jika item favorit ada di stok saat ini...
            if item_name in current_stock_map:
                now = datetime.now(timezone.utc)
                last_notif_time_str = last_notified_map.get(item_name)
                
                # Tentukan durasi "snooze" berdasarkan kategori
                item_category = current_stock_map[item_name]
                snooze_minutes = 30 if item_category == 'egg' else 5

                should_send = True
                if last_notif_time_str:
                    last_notif_time = datetime.fromisoformat(last_notif_time_str)
                    time_since_last_notif = now - last_notif_time
                    # Jika waktu sekarang kurang dari waktu snooze, JANGAN kirim notif
                    if time_since_last_notif < timedelta(minutes=snooze_minutes):
                        should_send = False
                        print(f"Notifikasi untuk '{item_name}' di-skip (masih dalam periode snooze).")

                if should_send:
                    if send_notification(fcm_token, item_name):
                        # Jika notifikasi berhasil dikirim, catat waktunya
                        last_notified_map[item_name] = now.isoformat()
                        did_update_timestamps = True

        # 5. Jika ada waktu yang diupdate, simpan kembali ke Firestore
        if did_update_timestamps:
            print(f"Memperbarui catatan waktu notifikasi untuk token {fcm_token[:10]}...")
            devices_ref.document(fcm_token).update({'last_notified': last_notified_map})

    print("--- Pengecekan Stok Selesai ---")