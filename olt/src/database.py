"""OLT Database - Inventory + Knowledge (Steps)"""
import sqlite3, json
from typing import Optional, List, Dict, Any

from .config import INFRA_DB

def init_db():
    conn = sqlite3.connect(INFRA_DB)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS olt_credentials (
                name TEXT PRIMARY KEY,
                host TEXT UNIQUE,
                user TEXT,
                password TEXT,
                vendor TEXT,
                model TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS olt_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT,
                syntax TEXT,
                description TEXT,
                execution_mode TEXT DEFAULT 'EXEC',
                sequence_json TEXT,
                UNIQUE(host, syntax)
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def list_inventory(host: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(INFRA_DB)
    conn.row_factory = sqlite3.Row
    try:
        if host:
            rows = conn.execute(
                "SELECT name, host, user, password, vendor, model FROM olt_credentials WHERE host = ?",
                (host,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT name, host, user, password, vendor, model FROM olt_credentials"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def list_knowledge(host: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(INFRA_DB)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT syntax, sequence_json as steps_json, description FROM olt_knowledge WHERE host = ?",
            (host,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            steps = json.loads(d.pop('steps_json'))
            d['steps'] = steps
            d['steps_count'] = len(steps)
            result.append(d)
        return result
    finally:
        conn.close()

def edit_inventory(action: str, data: Dict[str, Any]) -> str:
    conn = sqlite3.connect(INFRA_DB)
    try:
        if action == "save":
            required = ['name', 'host', 'user', 'password', 'vendor', 'model']
            for field in required:
                if field not in data or not data[field]:
                    return f"Error: '{field}' is mandatory for inventory"
            conn.execute('''
                INSERT INTO olt_credentials (name, host, user, password, vendor, model)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    host=excluded.host, user=excluded.user, password=excluded.password,
                    vendor=excluded.vendor, model=excluded.model
            ''', (
                data['name'], data['host'], data['user'], data['password'],
                data['vendor'], data['model']
            ))
            conn.commit()
            return f"Success: Inventory '{data['name']}' saved"
        elif action == "delete":
            if 'name' not in data: return "Error: 'name' is mandatory for delete"
            conn.execute("DELETE FROM olt_credentials WHERE name = ?", (data['name'],))
            conn.commit()
            return f"Success: Inventory '{data['name']}' deleted"
        return f"Error: Unknown action '{action}'"
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

def edit_knowledge(action: str, host: str, name: str,
                   steps: List[str] = None, description: str = "") -> str:
    conn = sqlite3.connect(INFRA_DB)
    try:
        if action == "save":
            if not steps: return "Error: 'steps' is mandatory"
            conn.execute('''
                INSERT INTO olt_knowledge (host, syntax, description, sequence_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(host, syntax) DO UPDATE SET
                    sequence_json=excluded.sequence_json, description=excluded.description
            ''', (host, name, description, json.dumps(steps)))
            conn.commit()
            return f"Success: Knowledge for '{name}' saved"
        elif action == "delete":
            conn.execute("DELETE FROM olt_knowledge WHERE host = ? AND syntax = ?", (host, name))
            conn.commit()
            return f"Success: Knowledge for '{name}' deleted"
        return f"Error: Unknown action '{action}'"
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

init_db()
