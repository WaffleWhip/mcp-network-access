import sqlite3
from typing import Optional, Any
from .config import ONT_DIR

def list_batches():
    return [f.name for f in ONT_DIR.glob("*.db")] if ONT_DIR.exists() else []

def get_summary(batch):
    db_path = ONT_DIR / batch
    if not db_path.exists(): return f"Error: Batch '{batch}' not found."
    conn = sqlite3.connect(db_path)
    try:
        t_ont = conn.execute('SELECT count(*) FROM units').fetchone()[0]
        t_cls = conn.execute('SELECT count(*) FROM cluster_stats').fetchone()[0]
        i_ont = conn.execute('SELECT sum(size) FROM cluster_stats WHERE size > 1').fetchone()[0] or 0
        return {"total_ont": t_ont, "total_clusters": t_cls, "impacted_onts": i_ont, "interference_ratio": f"{(i_ont/t_ont)*100:.2f}%"}
    finally: conn.close()

def get_clusters(batch, min_size=2):
    db_path = ONT_DIR / batch
    if not db_path.exists(): return "Error: Batch not found"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        query = 'SELECT cluster_id, size FROM cluster_stats WHERE size >= ? ORDER BY size DESC'
        return [dict(r) for r in conn.execute(query, (min_size,)).fetchall()]
    finally: conn.close()

def get_details(batch, cluster_id):
    db_path = ONT_DIR / batch
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        sns = [r[0] for r in conn.execute('SELECT sn FROM cluster_map WHERE cluster_id = ?', (cluster_id,)).fetchall()]
        if not sns: return "Error: Cluster not found."
        placeholders = ','.join(['?'] * len(sns))
        members = [dict(r) for r in conn.execute(f'SELECT sn, ch2g, ch5g FROM units WHERE sn IN ({placeholders})', sns).fetchall()]
        matrix = [dict(r) for r in conn.execute(f'SELECT n.parent_sn as "from", v.sn as "to", n.ssid, n.channel, n.signal FROM neighbors n JOIN unit_vaps v ON n.bssid = v.bssid WHERE n.parent_sn IN ({placeholders}) AND v.sn IN ({placeholders})', sns + sns).fetchall()]
        return {"members": members, "interference_matrix": matrix}
    finally: conn.close()

def get_status(batch, sn):
    db_path = ONT_DIR / batch
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        sn = sn.upper()
        unit = conn.execute('SELECT * FROM units WHERE sn = ?', (sn,)).fetchone()
        if not unit: return f"Error: ONT '{sn}' not found."
        c_id = (conn.execute('SELECT cluster_id FROM cluster_map WHERE sn = ?', (sn,)).fetchone() or [None])[0]
        neighs = [dict(r) for r in conn.execute('SELECT ssid, bssid, signal, channel FROM neighbors WHERE parent_sn = ?', (sn,)).fetchall()]
        vaps = [dict(r) for r in conn.execute('SELECT bssid FROM unit_vaps WHERE sn = ?', (sn,)).fetchall()]
        return {"sn": sn, "cluster_id": c_id, "config": {"ch2g": unit['ch2g'], "ch5g": unit['ch5g'], "my_macs": [v['bssid'] for v in vaps]}, "all_neighbors": neighs}
    finally: conn.close()
