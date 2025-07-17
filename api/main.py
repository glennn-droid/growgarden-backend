import os
import json
import firebase_admin
from firebase_admin import credentials
from flask import Flask, jsonify
from .scraper import get_current_stock
from .item_database import ALL_POSSIBLE_ITEMS
from .worker import check_stock_and_notify

# Mengambil kredensial dari Vercel Environment Variables
# Pastikan kamu sudah set 'FIREBASE_CREDENTIALS' di dashboard Vercel
cred_json_str = os.environ.get('FIREBASE_CREDENTIALS')

# Inisialisasi Firebase hanya jika kredensial ada
if cred_json_str and not firebase_admin._apps:
    cred_dict = json.loads(cred_json_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def home():
    return "Grow a Garden Notifier API is running."

@app.route("/api/stock")
def get_live_stock_endpoint():
    stock_list = get_current_stock()
    return jsonify({"in_stock": stock_list})

@app.route("/api/all-items")
def get_all_possible_items_endpoint():
    return jsonify(ALL_POSSIBLE_ITEMS)
    
@app.route("/api/trigger-worker")
def trigger_worker_endpoint():
    # Pengecekan sederhana untuk memastikan ini dipanggil oleh layanan terpercaya
    # Di aplikasi nyata, ini bisa menggunakan secret key
    print("Memicu worker dari endpoint...")
    check_stock_and_notify()
    return jsonify({"status": "worker triggered"}), 200