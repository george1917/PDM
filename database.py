import sqlite3
from datetime import datetime
import pandas as pd
from typing import List, Optional, Dict, Any

DB_NAME = "pdm.db"

def get_connection():
    """建立並回傳資料庫連線"""
    return sqlite3.connect(DB_NAME)

def init_db():
    """初始化資料庫與 Table，並自動遷移 Schema"""
    conn = get_connection()
    c = conn.cursor()
    
    # 建立表格 (如果完全不存在)
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            category TEXT,
            price REAL,
            cost REAL,
            description TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 簡易 Migration: 檢查 image_path 是否存在，若無則新增
    try:
        c.execute("SELECT image_path FROM products LIMIT 1")
    except sqlite3.OperationalError:
        # 欄位不存在，執行 Alter Table
        print("Migrating database: adding image_path column...")
        c.execute("ALTER TABLE products ADD COLUMN image_path TEXT")
    
    conn.commit()
    conn.close()

def add_product(name: str, sku: str, category: str, price: float, cost: float, description: str, image_path: Optional[str] = None) -> bool:
    """新增產品，若 SKU 重複則回傳 False"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO products (name, sku, category, price, cost, description, image_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, sku, category, price, cost, description, image_path, datetime.now()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # SKU duplications
        return False
    except Exception as e:
        print(f"Error adding product: {e}")
        return False
    finally:
        conn.close()

def get_product_by_id(product_id: int) -> Optional[tuple]:
    """依 ID 取得單筆產品資料"""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return c.fetchone()
    finally:
        conn.close()

def get_product_by_sku(sku: str) -> Optional[tuple]:
    """依 SKU 取得單筆產品資料"""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE sku = ?", (sku,))
        return c.fetchone()
    finally:
        conn.close()

def update_product(product_id: int, name: str, sku: str, category: str, price: float, cost: float, description: str, image_path: Optional[str] = None) -> bool:
    """更新產品資料"""
    try:
        conn = get_connection()
        c = conn.cursor()
        
        if image_path:
             c.execute('''
                UPDATE products 
                SET name=?, sku=?, category=?, price=?, cost=?, description=?, image_path=?
                WHERE id=?
            ''', (name, sku, category, price, cost, description, image_path, product_id))
        else:
             c.execute('''
                UPDATE products 
                SET name=?, sku=?, category=?, price=?, cost=?, description=?
                WHERE id=?
            ''', (name, sku, category, price, cost, description, product_id))
            
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # SKU duplications might happen if user changes SKU to existing one
        return False
    except Exception as e:
        print(f"Error updating product: {e}")
        return False
    finally:
        conn.close()

def get_all_products() -> pd.DataFrame:
    """取得所有產品資料，回傳 DataFrame 以利顯示"""
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM products ORDER BY created_at DESC", conn)
        return df
    finally:
        conn.close()

def delete_product(product_id: int) -> bool:
    """刪除指定 ID 的產品"""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting product: {e}")
        return False
    finally:
        conn.close()
