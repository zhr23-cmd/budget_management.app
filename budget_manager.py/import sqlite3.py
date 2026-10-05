import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "budget.db"

def init_db():
    """Veritabanini ve gerekli tabloyu oluşturur."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,       -- 'Gelir' veya 'Gider'
            category TEXT NOT NULL,   -- 'Kira', 'Mutfak', 'Maas' vb.
            amount REAL NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_transaction(date_str, trans_type, category, amount, description=""):
    """Yeni bir gelir veya gider kaydi ekler."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (date, type, category, amount, description)
        VALUES (?, ?, ?, ?, ?)
    """, (date_str, trans_type, category, amount, description))
    conn.commit()
    conn.close()

def get_all_transactions():
    """Tüm kayitlari Pandas DataFrame olarak getirir."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC", conn)
    conn.close()
    return df

def delete_transaction(trans_id):
    """ID değerine göre kayit siler."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
    conn.commit()
    conn.close()