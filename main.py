from flask import Flask, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "crm_secret_key_123"

DB = "crm.db"
ADMIN_PASSWORD = "1234"

# Initialize DB on startup
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            service TEXT,
            notes TEXT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            date TEXT,
            time TEXT,
            service TEXT,
            notes TEXT
        )
    ''')

    conn.commit()
    conn.close()

# 🟢 תריץ את זה כאן — לא בתוך __main__
init_db()
