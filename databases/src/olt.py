import sqlite3
from typing import Optional, Any
from .config import INFRA_DB

def list_olts():
    conn = sqlite3.connect(INFRA_DB)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute('SELECT name, host, user, password, vendor, model FROM olt_credentials').fetchall()]
    finally: conn.close()

def save_olt(name, host, user, password, vendor, model):
    if not all([name, host, user, password]): return "Error: name, host, user, password required"
    conn = sqlite3.connect(INFRA_DB)
    try:
        conn.execute('INSERT INTO olt_credentials VALUES (?,?,?,?,?,?) ON CONFLICT(name) DO UPDATE SET host=excluded.host, user=excluded.user, password=excluded.password, vendor=excluded.vendor, model=excluded.model', 
                     (name.upper(), host, user, password, vendor.lower() if vendor else None, model))
        conn.commit()
        return f"Success: OLT '{name}' saved."
    finally: conn.close()

def delete_olt(name):
    if not name: return "Error: name required"
    conn = sqlite3.connect(INFRA_DB)
    try:
        conn.execute('DELETE FROM olt_credentials WHERE name=?', (name.upper(),))
        conn.commit()
        return f"Success: OLT '{name}' deleted."
    finally: conn.close()

def list_cmds(vendor=None, model=None):
    conn = sqlite3.connect(INFRA_DB)
    conn.row_factory = sqlite3.Row
    try:
        v = vendor.lower() if vendor else None
        if v and model:
            rows = conn.execute('SELECT command_syntax, execution_mode, description FROM olt_commands WHERE vendor=? AND model=?', (v, model)).fetchall()
            return {"type": "commands", "vendor": v, "model": model, "data": [dict(r) for r in rows]}
        elif v:
            rows = conn.execute('SELECT DISTINCT model FROM olt_commands WHERE vendor=?', (v,)).fetchall()
            return {"type": "models", "vendor": v, "available_models": [r['model'] for r in rows if r['model']]}
        else:
            rows = conn.execute('SELECT DISTINCT vendor FROM olt_commands').fetchall()
            return {"type": "brands", "available_brands": [r['vendor'] for r in rows]}
    finally: conn.close()

def save_cmd(vendor, model, command_syntax, execution_mode, description):
    """
    Saves a CLI command. ALL parameters are mandatory to ensure database quality.
    """
    if not all([vendor, model, command_syntax, execution_mode, description]):
        return "Error: ALL parameters (vendor, model, command_syntax, execution_mode, description) are MANDATORY."
    
    conn = sqlite3.connect(INFRA_DB)
    try:
        conn.execute('''
            INSERT INTO olt_commands (vendor, model, command_syntax, execution_mode, description) 
            VALUES (?,?,?,?,?) 
            ON CONFLICT(vendor, model, command_syntax) 
            DO UPDATE SET execution_mode=excluded.execution_mode, description=excluded.description
        ''', (vendor.lower(), model, command_syntax, execution_mode, description))
        conn.commit()
        return f"Success: Command '{command_syntax}' with description saved for {vendor} {model}."
    except Exception as e:
        return f"Error saving command: {str(e)}"
    finally: 
        conn.close()
