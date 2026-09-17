import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("data/ai_ops.db")
DB_PATH.parent.mkdir(exist_ok=True)

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            service TEXT NOT NULL,
            severity TEXT NOT NULL,
            alert TEXT NOT NULL,
            environment TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            approval_id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            approved_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT NOT NULL,
            event TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

def now():
    return datetime.now(timezone.utc).isoformat()

def save_incident(data):
    with _conn() as c:
        c.execute(
            "INSERT INTO incidents VALUES (?,?,?,?,?,?,?)",
            (data["incident_id"], data["service"], data["severity"],
             data["alert"], data["environment"], data["status"], now())
        )

def save_approval(approval_id, incident_id, action):
    with _conn() as c:
        c.execute(
            "INSERT INTO approvals VALUES (?,?,?,?,?,?,?)",
            (approval_id, incident_id, action, "pending", None, now(), now())
        )

def get_approval(approval_id):
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM approvals WHERE approval_id=?", (approval_id,)
        ).fetchone()
        return dict(row) if row else None

def update_approval(approval_id, approved, approved_by):
    status = "approved" if approved else "rejected"
    with _conn() as c:
        c.execute(
            "UPDATE approvals SET status=?, approved_by=?, updated_at=? WHERE approval_id=?",
            (status, approved_by, now(), approval_id)
        )

def audit(incident_id, event, payload):
    with _conn() as c:
        c.execute(
            "INSERT INTO audit (incident_id,event,payload,created_at) VALUES (?,?,?,?)",
            (incident_id, event, json.dumps(payload), now())
        )
