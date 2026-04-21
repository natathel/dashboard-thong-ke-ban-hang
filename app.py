from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

APP_TITLE = 'Dashboard Thống Kê Bán Hàng'
DATABASE = Path(os.environ.get('APP_DATABASE', Path(__file__).with_name('app.db')))
SCHEMA_SQL = "\nCREATE TABLE IF NOT EXISTS customers (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    name TEXT NOT NULL,\n    email TEXT UNIQUE NOT NULL\n);\nCREATE TABLE IF NOT EXISTS orders (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,\n    product_name TEXT NOT NULL,\n    quantity INTEGER NOT NULL,\n    unit_price REAL NOT NULL,\n    status TEXT NOT NULL DEFAULT 'paid',\n    ordered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP\n);\n"
SEED_CODE = "\nconn.executemany('INSERT INTO customers(name, email) VALUES (?, ?)', [\n    ('An Nguyễn', 'an@example.com'),\n    ('Bình Trần', 'binh@example.com'),\n    ('Chi Lê', 'chi@example.com'),\n])\norders = []\nproducts = [('Gói Basic', 1, 199000), ('Gói Pro', 2, 399000), ('Tư vấn triển khai', 1, 1200000), ('Gói Pro', 1, 399000)]\nfor idx in range(18):\n    product_name, quantity, unit_price = products[idx % len(products)]\n    orders.append(((idx % 3) + 1, product_name, quantity, unit_price, 'paid'))\nconn.executemany('INSERT INTO orders(customer_id, product_name, quantity, unit_price, status) VALUES (?, ?, ?, ?, ?)', orders)\n"
ITEMS_SQL = 'SELECT orders.id, customers.name AS customer, product_name, quantity, unit_price,\nquantity * unit_price AS total, status, ordered_at\nFROM orders JOIN customers ON customers.id = orders.customer_id\nORDER BY orders.id DESC LIMIT ?'


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def scalar(sql: str, params: tuple[Any, ...] = ()) -> Any:
    with closing(get_connection()) as conn:
        return conn.execute(sql, params).fetchone()[0]


def query_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with closing(get_connection()) as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def execute(sql: str, params: tuple[Any, ...] = ()) -> int:
    with closing(get_connection()) as conn:
        cursor = conn.execute(sql, params)
        conn.commit()
        return int(cursor.lastrowid)


def init_db(seed: bool = True) -> None:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection()) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    if seed:
        seed_db()


def seed_db() -> None:
    with closing(get_connection()) as conn:
        table_count = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
        data_count = 0
        for table in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall():
            data_count += conn.execute(f"SELECT COUNT(*) FROM {table['name']}").fetchone()[0]
        if table_count and data_count:
            return
        exec(SEED_CODE, {'conn': conn})
        conn.commit()


def build_stats() -> dict[str, Any]:

    return {
        'orders': scalar('SELECT COUNT(*) FROM orders'),
        'customers': scalar('SELECT COUNT(*) FROM customers'),
        'revenue': round(float(scalar("SELECT SUM(quantity * unit_price) FROM orders WHERE status = 'paid'") or 0), 2),
        'avg_order': round(float(scalar("SELECT AVG(quantity * unit_price) FROM orders WHERE status = 'paid'") or 0), 2),
    }


def latest_rows(limit: int = 20) -> list[dict[str, Any]]:
    return query_all(ITEMS_SQL, (limit,))


def create_app() -> Flask:
    app = Flask(__name__)
    init_db(seed=True)

    @app.get('/')
    def index():
        return render_template('index.html', title=APP_TITLE, stats=build_stats(), rows=latest_rows())

    @app.get('/health')
    def health():
        return jsonify({'status': 'ok', 'title': APP_TITLE, 'database': str(DATABASE)})

    @app.get('/api/stats')
    def api_stats():
        return jsonify(build_stats())

    @app.get('/api/items')
    def api_items():
        return jsonify(latest_rows(limit=int(request.args.get('limit', 20))))


    @app.get('/api/top-products')
    def top_products():
        rows = query_all('SELECT product_name, SUM(quantity) AS sold, SUM(quantity * unit_price) AS revenue FROM orders GROUP BY product_name ORDER BY revenue DESC')
        return jsonify(rows)
    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5004)), debug=True)
