import sqlite3
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "data" / "store_forward.db"


def init_queue():
    """Create the local SQLite queue if it does not exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS return_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_id TEXT UNIQUE NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued'
            )
            """
        )
        conn.commit()


def enqueue_return(record):
    """Store a return locally when the network is unavailable."""
    init_queue()

    return_id = str(record.get("return_id", "")).strip()

    if not return_id:
        raise ValueError("return_id is required")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO return_queue
            (return_id, payload, status)
            VALUES (?, ?, 'queued')
            """,
            (
                return_id,
                json.dumps(record),
            ),
        )
        conn.commit()

    return {
        "return_id": return_id,
        "status": "queued",
    }


def get_queued_returns():
    """Read returns waiting in the local queue."""
    init_queue()

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT return_id, payload
            FROM return_queue
            WHERE status = 'queued'
            ORDER BY id
            """
        ).fetchall()

    return [
        {
            "return_id": return_id,
            **json.loads(payload),
        }
        for return_id, payload in rows
    ]


def process_queue():
    """Forward all queued returns after the network is restored."""
    init_queue()

    queued = get_queued_returns()

    with sqlite3.connect(DB_PATH) as conn:
        for item in queued:
            conn.execute(
                """
                UPDATE return_queue
                SET status = 'processed'
                WHERE return_id = ?
                """,
                (item["return_id"],),
            )

        conn.commit()

    return {
        "processed_count": len(queued),
        "processed_return_ids": [
            item["return_id"] for item in queued
        ],
    }


def queue_status():
    """Return counts for queued and processed records."""
    init_queue()

    with sqlite3.connect(DB_PATH) as conn:
        queued = conn.execute(
            """
            SELECT COUNT(*)
            FROM return_queue
            WHERE status = 'queued'
            """
        ).fetchone()[0]

        processed = conn.execute(
            """
            SELECT COUNT(*)
            FROM return_queue
            WHERE status = 'processed'
            """
        ).fetchone()[0]

    return {
        "queued": queued,
        "processed": processed,
    }