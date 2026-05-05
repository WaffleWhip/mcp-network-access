"""OLT Database - Inventory + Knowledge (Steps)"""

import sqlite3, json
from typing import Optional, List, Dict, Any

from .config import INFRA_DB


def init_db():
    conn = sqlite3.connect(INFRA_DB)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS olt_credentials (
                name TEXT PRIMARY KEY,
                host TEXT UNIQUE,
                user TEXT,
                password TEXT,
                vendor TEXT,
                model TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS olt_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT,
                syntax TEXT,
                description TEXT,
                execution_mode TEXT DEFAULT 'EXEC',
                sequence_json TEXT,
                UNIQUE(host, syntax)
            )
        """)
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
                (host,),
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
            "SELECT syntax, sequence_json as hint_json, description FROM olt_knowledge WHERE host = ?",
            (host,),
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            hint_list = json.loads(d.pop("hint_json"))
            d["hint"] = hint_list
            d["hint_count"] = len(hint_list)
            result.append(d)
        return result
    finally:
        conn.close()


def edit_inventory(action: str, data: Dict[str, Any]) -> str:
    conn = sqlite3.connect(INFRA_DB)
    try:
        if action == "save":
            required = ["name", "host", "user", "password", "vendor", "model"]
            for field in required:
                if field not in data or not data[field]:
                    return f"Error: '{field}' is mandatory for inventory"
            name = data["name"]
            host = data["host"]
            existing_by_name = conn.execute(
                "SELECT host FROM olt_credentials WHERE name = ?", (name,)
            ).fetchone()
            if existing_by_name and existing_by_name[0] != host:
                return f"Error: Name '{name}' already exists with IP {existing_by_name[0]}. Use a different name or edit to update IP."
            existing_by_host = conn.execute(
                "SELECT name FROM olt_credentials WHERE host = ?", (host,)
            ).fetchone()
            if existing_by_host and existing_by_host[0] != name:
                return f"Error: IP {host} already registered as '{existing_by_host[0]}'. Delete that entry first or use a different name."
            conn.execute(
                """
                INSERT INTO olt_credentials (name, host, user, password, vendor, model)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    host=excluded.host, user=excluded.user, password=excluded.password,
                    vendor=excluded.vendor, model=excluded.model
            """,
                (
                    name,
                    host,
                    data["user"],
                    data["password"],
                    data["vendor"],
                    data["model"],
                ),
            )
            conn.commit()
            return f"Success: Inventory '{name}' saved"
        elif action == "update":
            if "name" not in data:
                return "Error: 'name' is mandatory for update"
            updates = []
            values = []
            for field in ["host", "user", "password", "vendor", "model"]:
                if field in data and data[field] is not None:
                    updates.append(f"{field}=excluded.{field}")
                    values.append(data[field])
            if not updates:
                return "Error: no fields to update"
            values.append(data["name"])
            conn.execute(
                f"""INSERT INTO olt_credentials (name, host, user, password, vendor, model)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET {", ".join(updates)}""",
                (
                    data["name"],
                    data.get("host"),
                    data.get("user"),
                    data.get("password"),
                    data.get("vendor"),
                    data.get("model"),
                ),
            )
            conn.commit()
            return f"Success: Inventory '{data['name']}' updated"
        elif action == "delete":
            if "host" not in data:
                return "Error: 'host' (IP) is mandatory for delete"
            deleted = conn.execute(
                "DELETE FROM olt_credentials WHERE host = ?", (data["host"],)
            ).rowcount
            conn.commit()
            if deleted == 0:
                return f"Error: No OLT found with IP {data['host']}"
            return f"Success: OLT with IP {data['host']} deleted"
        return f"Error: Unknown action '{action}'"
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()


def edit_knowledge(
    action: str,
    host: str,
    syntax: str = None,
    hint: List[str] = None,
    description: str = "",
) -> str:
    conn = sqlite3.connect(INFRA_DB)
    try:
        if action == "save":
            hint = hint or []
            description = description or ""

            if syntax and syntax.strip().lower() not in ("null", ""):
                syntax_clean = syntax.strip()
            elif hint:
                syntax_clean = hint[-1] if hint else ""
            elif description:
                syntax_clean = description.split()[0] if description.split() else ""
            else:
                return (
                    "Error: 'syntax' is required (provide syntax, hint, or description)"
                )

            if not syntax_clean:
                return (
                    "Error: 'syntax' is required (provide syntax, hint, or description)"
                )

            conn.execute(
                """
                INSERT INTO olt_knowledge (host, syntax, description, sequence_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(host, syntax) DO UPDATE SET
                    sequence_json=excluded.sequence_json, description=excluded.description
            """,
                (host, syntax_clean, description, json.dumps(hint)),
            )
            conn.commit()
            return f"Success: Knowledge for '{syntax_clean}' saved"
        elif action == "update":
            if not syntax:
                return "Error: 'syntax' is required for update"
            hint = hint if hint is not None else []
            conn.execute(
                """INSERT INTO olt_knowledge (host, syntax, description, sequence_json)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(host, syntax) DO UPDATE SET
                       description=excluded.description, sequence_json=excluded.sequence_json""",
                (host, syntax, description or "", json.dumps(hint)),
            )
            conn.commit()
            return f"Success: Knowledge for '{syntax}' updated"
        elif action == "delete":
            if not syntax:
                return "Error: 'syntax' is required for delete"
            conn.execute(
                "DELETE FROM olt_knowledge WHERE host = ? AND syntax = ?",
                (host, syntax),
            )
            conn.commit()
            return f"Success: Knowledge for '{syntax}' deleted"
        return f"Error: Unknown action '{action}'"
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()


def find_hint(host: str, syntax: str) -> Optional[List[str]]:
    """Find hint for syntax using prefix matching. 'show card 1/1' → hint from 'show card'."""
    conn = sqlite3.connect(INFRA_DB)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT syntax, sequence_json FROM olt_knowledge WHERE host = ?",
            (host,),
        ).fetchall()
        syntax_lower = syntax.lower()
        for row in rows:
            base = row["syntax"]
            if syntax_lower.startswith(base.lower()) or base.lower() in syntax_lower:
                hint_list = json.loads(row["sequence_json"])
                return hint_list
        return None
    finally:
        conn.close()


def resolve_syntax(host: str, syntax: str) -> Optional[Dict[str, Any]]:
    """Find syntax entry using prefix matching. Returns full row or None."""
    conn = sqlite3.connect(INFRA_DB)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT syntax, sequence_json, description FROM olt_knowledge WHERE host = ?",
            (host,),
        ).fetchall()
        syntax_lower = syntax.lower()
        for row in rows:
            base = row["syntax"]
            if syntax_lower.startswith(base.lower()) or base.lower() in syntax_lower:
                return {
                    "syntax": row["syntax"],
                    "hint": json.loads(row["sequence_json"]),
                    "description": row["description"],
                }
        return None
    finally:
        conn.close()


init_db()
