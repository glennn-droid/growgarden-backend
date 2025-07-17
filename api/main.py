# api/main.py (Versi Final Flask)
import os
import json
import firebase_admin
from firebase_admin import credentials
from flask import Flask, jsonify
from .scraper import get_current_stock       # Perhatikan titik di depan scraper
from .item_database import ALL_POSSIBLE_ITEMS # Perhatikan titik di depan item_database
from .worker import check_stock_and_notify    # Perhatikan titik di depan worker

# Inisialisasi Firebase
if not firebase_admin._apps:
    # Kita tidak bisa membaca secret di level atas Vercel, jadi kita baca filenya
    # Pastikan firebase-credentials.json ada di folder /api
    cred = credentials.Certificate("api/firebase-credentials.json")
    firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def read_root():
    return jsonify({"message": "Welcome to GrowGarden Notifier API"})

@app.route("/api/stock")
def get_live_stock():
    stock_list = get_current_stock()
    return jsonify({"in_stock": stock_list})

@app.route("/api/all-items")
def get_all_possible_items():
    return jsonify(ALL_POSSIBLE_ITEMS)

@app.route("/api/trigger-worker")
def trigger_worker_endpoint():
    check_stock_and_notify()
    return jsonify({"status": "worker triggered"}), 200