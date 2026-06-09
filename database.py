# database.py
## Core database layer structured by Janssen
import sqlite3, os
from datetime import date
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "umkm_finance.db")

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    c.execute("PRAGMA journal_mode = WAL")
    return c

def init_db():
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS accounts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, type TEXT NOT NULL,
                balance REAL DEFAULT 0, color TEXT DEFAULT '#6366F1',
                icon TEXT DEFAULT '🏦',
                created_at TEXT DEFAULT (datetime('now','localtime')));
            CREATE TABLE IF NOT EXISTS categories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, type TEXT NOT NULL,
                icon TEXT DEFAULT '📦', color TEXT DEFAULT '#6366F1');
            CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL, type TEXT NOT NULL, amount REAL NOT NULL,
                category_id INTEGER REFERENCES categories(id),
                account_id  INTEGER REFERENCES accounts(id),
                description TEXT, note TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime')));
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
        """)
        if c.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
            c.executemany("INSERT INTO categories(name,type,icon,color) VALUES(?,?,?,?)", [
                ("Penjualan Produk","income","🛍️","#10B981"),
                ("Jasa / Layanan",  "income","💼","#3B82F6"),
                ("Investasi",       "income","📈","#6366F1"),
                ("Pendapatan Lain", "income","💰","#F59E0B"),
                ("Pembelian Bahan", "expense","🛒","#EF4444"),
                ("Gaji Karyawan",   "expense","👷","#F97316"),
                ("Sewa & Utilitas", "expense","🏠","#8B5CF6"),
                ("Marketing",       "expense","📣","#EC4899"),
                ("Operasional",     "expense","⚙️","#6B7280"),
                ("Lain-lain",       "expense","📦","#9CA3AF"),
            ])
        c.executemany("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", [
            ("business_name","UMKM Saya"),("owner_name","Pemilik"),
            ("business_type","—"),("phone","—"),("email","—"),("address","—"),
        ])

# ── Accounts ──────────────────────────────────────────────────────
def get_accounts() -> List[Dict]:
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM accounts ORDER BY name")]

def add_account(name, type_, balance, color, icon) -> int:
    with _conn() as c:
        cur = c.execute("INSERT INTO accounts(name,type,balance,color,icon) VALUES(?,?,?,?,?)",
                        (name,type_,float(balance),color,icon))
        return cur.lastrowid

def update_account(id_, name, type_, balance, color, icon):
    with _conn() as c:
        c.execute("UPDATE accounts SET name=?,type=?,balance=?,color=?,icon=? WHERE id=?",
                  (name,type_,float(balance),color,icon,id_))

def delete_account(id_: int):
    with _conn() as c:
        c.execute("DELETE FROM accounts WHERE id=?", (id_,))

# ── Categories ────────────────────────────────────────────────────
def get_categories(type_: Optional[str]=None) -> List[Dict]:
    with _conn() as c:
        if type_:
            rows = c.execute("SELECT * FROM categories WHERE type=? ORDER BY name",(type_,))
        else:
            rows = c.execute("SELECT * FROM categories ORDER BY type,name")
        return [dict(r) for r in rows]

def add_category(name, type_, icon, color) -> int:
    with _conn() as c:
        cur = c.execute("INSERT INTO categories(name,type,icon,color) VALUES(?,?,?,?)",
                        (name,type_,icon,color))
        return cur.lastrowid

def delete_category(id_: int):
    with _conn() as c:
        c.execute("DELETE FROM categories WHERE id=?", (id_,))

# ── Transactions ──────────────────────────────────────────────────
def get_transactions(limit=100, offset=0, type_=None, month=None, search=None) -> List[Dict]:
    where, params = [], []
    if type_:   where.append("t.type=?");                    params.append(type_)
    if month:   where.append("strftime('%Y-%m',t.date)=?");  params.append(month)
    if search:  where.append("(t.description LIKE ? OR t.note LIKE ?)"); params+=[f"%{search}%"]*2
    clause = ("WHERE "+" AND ".join(where)) if where else ""
    sql = f"""SELECT t.*, c.name AS cat_name, c.icon AS cat_icon, c.color AS cat_color,
                     a.name AS acc_name, a.icon AS acc_icon
              FROM transactions t
              LEFT JOIN categories c ON t.category_id=c.id
              LEFT JOIN accounts   a ON t.account_id =a.id
              {clause} ORDER BY t.date DESC,t.id DESC LIMIT ? OFFSET ?"""
    params += [limit, offset]
    with _conn() as c:
        return [dict(r) for r in c.execute(sql, params)]

def add_transaction(date_, type_, amount, category_id, account_id, description, note="") -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO transactions(date,type,amount,category_id,account_id,description,note) VALUES(?,?,?,?,?,?,?)",
            (date_, type_, float(amount), category_id, account_id, description, note))
        delta = float(amount) if type_=="income" else -float(amount)
        c.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (delta, account_id))
        return cur.lastrowid

def update_transaction(id_, date_, type_, amount, category_id, account_id, description, note=""):
    with _conn() as c:
        old = c.execute("SELECT type,amount,account_id FROM transactions WHERE id=?", (id_,)).fetchone()
        if old:
            old_delta = float(old["amount"]) if old["type"]=="income" else -float(old["amount"])
            c.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (-old_delta, old["account_id"]))
        c.execute("""UPDATE transactions SET date=?,type=?,amount=?,category_id=?,
                     account_id=?,description=?,note=? WHERE id=?""",
                  (date_, type_, float(amount), category_id, account_id, description, note, id_))
        new_delta = float(amount) if type_=="income" else -float(amount)
        c.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (new_delta, account_id))

def delete_transaction(id_: int):
    with _conn() as c:
        old = c.execute("SELECT type,amount,account_id FROM transactions WHERE id=?", (id_,)).fetchone()
        if old:
            delta = float(old["amount"]) if old["type"]=="income" else -float(old["amount"])
            c.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (-delta, old["account_id"]))
        c.execute("DELETE FROM transactions WHERE id=?", (id_,))

def delete_all_transactions():
    with _conn() as c:
        c.execute("DELETE FROM transactions")
        c.execute("UPDATE accounts SET balance=0")

# ── Analytics ─────────────────────────────────────────────────────
def get_summary(month=None) -> Dict:
    clause = "WHERE strftime('%Y-%m',date)=?" if month else ""
    params = [month] if month else []
    with _conn() as c:
        r = c.execute(f"""SELECT
            COALESCE(SUM(CASE WHEN type='income'  THEN amount END),0) AS income,
            COALESCE(SUM(CASE WHEN type='expense' THEN amount END),0) AS expense,
            COUNT(*) AS txn_count FROM transactions {clause}""", params).fetchone()
        inc,exp = float(r["income"]), float(r["expense"])
        return {"income":inc,"expense":exp,"profit":inc-exp,"txn_count":r["txn_count"]}

def get_monthly_trend(months=6) -> List[Dict]:
    with _conn() as c:
        rows = c.execute(f"""SELECT strftime('%Y-%m',date) AS month,
            COALESCE(SUM(CASE WHEN type='income'  THEN amount END),0) AS income,
            COALESCE(SUM(CASE WHEN type='expense' THEN amount END),0) AS expense
            FROM transactions GROUP BY month ORDER BY month DESC LIMIT ?""",(months,)).fetchall()
        return [dict(r) for r in reversed(rows)]

def get_category_breakdown(type_, month=None) -> List[Dict]:
    extra = "AND strftime('%Y-%m',t.date)=?" if month else ""
    params = [type_]+([month] if month else [])
    with _conn() as c:
        rows = c.execute(f"""SELECT c.name,c.icon,c.color,
            COALESCE(SUM(t.amount),0) AS total
            FROM transactions t LEFT JOIN categories c ON t.category_id=c.id
            WHERE t.type=? {extra} GROUP BY c.id ORDER BY total DESC""", params).fetchall()
        return [dict(r) for r in rows]

def get_daily_cashflow(days=14) -> List[Dict]:
    with _conn() as c:
        rows = c.execute(f"""SELECT date,
            COALESCE(SUM(CASE WHEN type='income'  THEN amount END),0) AS income,
            COALESCE(SUM(CASE WHEN type='expense' THEN amount END),0) AS expense
            FROM transactions WHERE date>=date('now','-{days} days')
            GROUP BY date ORDER BY date""").fetchall()
        return [dict(r) for r in rows]

# ── Settings ──────────────────────────────────────────────────────
def get_setting(key, default="") -> str:
    with _conn() as c:
        r = c.execute("SELECT value FROM settings WHERE key=?",(key,)).fetchone()
        return r["value"] if r else default

def set_setting(key, value):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",(key,value))
