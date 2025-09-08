# tag_store.py
import sqlite3, binascii
from datetime import datetime

class TagStore:
    def __init__(self, path="rfid_tags.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS tags(
          tag_key   INTEGER PRIMARY KEY,
          uid_hex   TEXT UNIQUE NOT NULL,
          message   TEXT,
          function  TEXT NOT NULL,
          updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_uid ON tags(uid_hex)")

    @staticmethod
    def _hex(uid_bytes) -> str:
        return binascii.hexlify(bytes(uid_bytes)).decode("ascii")

    def upsert(self, tag_key:int, uid_bytes:bytes, message:str, function:str):
        uid_hex = self._hex(uid_bytes)
        self.conn.execute("""
        INSERT INTO tags(tag_key, uid_hex, message, function, updated_at)
        VALUES(?, ?, ?, ?, ?)
        ON CONFLICT(tag_key) DO UPDATE SET
          uid_hex=excluded.uid_hex,
          message=excluded.message,
          function=excluded.function,
          updated_at=excluded.updated_at
        """, (tag_key, uid_hex, message, function, datetime.utcnow().isoformat()))
        self.conn.commit()

    def copy_tag(self, old_uid_bytes:bytes, new_uid_bytes:bytes):
        old_uid_hex = self._hex(old_uid_bytes)
        row = self.conn.execute(
            "SELECT tag_key, message, function FROM tags WHERE uid_hex=?",
            (old_uid_hex,)
        ).fetchone()
        if not row:
            return None
        old_key, msg, func = row
        (max_key,) = self.conn.execute("SELECT COALESCE(MAX(tag_key),0) FROM tags").fetchone()
        new_key = max_key + 1
        self.upsert(new_key, new_uid_bytes, msg, func)
        return (old_key, new_key)

    def get_by_uid(self, uid_bytes:bytes):
        uid_hex = self._hex(uid_bytes)
        return self.conn.execute(
            "SELECT tag_key, message, function FROM tags WHERE uid_hex=?",
            (uid_hex,)
        ).fetchone()

    def get_by_key(self, tag_key:int):
        return self.conn.execute(
            "SELECT tag_key, uid_hex, message, function FROM tags WHERE tag_key=?",
            (tag_key,)
        ).fetchone()

    def next_free_key(self) -> int:
        (max_key,) = self.conn.execute("SELECT COALESCE(MAX(tag_key),0) FROM tags").fetchone()
        return (max_key or 0) + 1

    def delete_by_uid(self, uid_bytes) -> int:
        uid_hex = self._hex(uid_bytes)
        cur = self.conn.execute("DELETE FROM tags WHERE uid_hex = ?", (uid_hex,))
        self.conn.commit()
        return cur.rowcount  # number of rows removed

    def delete_by_key(self, tag_key:int) -> int:
        cur = self.conn.execute("DELETE FROM tags WHERE tag_key = ?", (tag_key,))
        self.conn.commit()
        return cur.rowcount
