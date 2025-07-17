# main.py

import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI
from scraper import get_current_stock
from item_database import ALL_POSSIBLE_ITEMS # <-- Import kamus kita

cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)

app = FastAPI()

# Pintu lama, tetap kita pakai nanti untuk notifikasi
@app.get("/api/stock")
def get_live_stock():
    stock_list = get_current_stock()
    return {"in_stock": stock_list}

# PINTU BARU: untuk memberikan daftar semua item ke aplikasi Flutter
@app.get("/api/all-items")
def get_all_possible_items():
    return ALL_POSSIBLE_ITEMS