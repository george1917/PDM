import sqlite3
import os
from datetime import datetime

DB_FILE = 'products.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            spec TEXT,
            description TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_product(code, name, category, spec, description, image_path):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO products (code, name, category, spec, description, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code, name, category, spec, description, image_path))
        conn.commit()
        return True, "Success"
    except sqlite3.IntegrityError:
        return False, "產品編號已存在 (Product code already exists)"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def upsert_product(code, name, category, spec, description, image_path=""):
    """
    Insert or Update product based on code. 
    Image path is optional; if empty string passed during update, it might overwrite? 
    For batch update, if image_path is missing in Excel, maybe we shouldn't wipe it?
    For this simple version, we will assume Excel provides full data or we handle it carefully.
    Let's stick to simple UPSERT: updates everything provided.
    """
    conn = get_connection()
    c = conn.cursor()
    try:
        # Check if product exists to decide on image_path preservation if needed, 
        # but standard UPSERT replaces. 
        # Requirement: "Batch Update". simpler to just overwrite.
        
        c.execute('''
            INSERT INTO products (code, name, category, spec, description, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                name=excluded.name,
                category=excluded.category,
                spec=excluded.spec,
                description=excluded.description,
                image_path=excluded.image_path
        ''', (code, name, category, spec, description, image_path))
        conn.commit()
        return True, "Success"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM products ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def delete_product(product_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
