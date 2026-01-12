from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class SessionState:
    def __init__(self, db_path: str = ".daggr_sessions.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                graph_name TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                node_name TEXT,
                port_name TEXT,
                value TEXT,
                updated_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS port_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                node_name TEXT,
                port_name TEXT,
                value TEXT,
                source_input TEXT,
                created_at TEXT,
                selected INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                node_name TEXT,
                result TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        conn.commit()
        conn.close()

    def create_session(self, graph_name: str) -> str:
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (session_id, graph_name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (session_id, graph_name, now, now),
        )
        conn.commit()
        conn.close()
        return session_id

    def get_or_create_session(self, session_id: Optional[str], graph_name: str) -> str:
        if session_id:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id FROM sessions WHERE session_id = ?", (session_id,)
            )
            result = cursor.fetchone()
            conn.close()
            if result:
                return session_id
        return self.create_session(graph_name)

    def save_input(self, session_id: str, node_name: str, port_name: str, value: Any):
        now = datetime.now().isoformat()
        value_json = json.dumps(value, default=str)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO node_inputs 
               (session_id, node_name, port_name, value, updated_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, node_name, port_name, value_json, now),
        )
        cursor.execute(
            "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
            (now, session_id),
        )
        conn.commit()
        conn.close()

    def get_inputs(self, session_id: str) -> Dict[str, Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT node_name, port_name, value FROM node_inputs WHERE session_id = ?",
            (session_id,),
        )
        results = cursor.fetchall()
        conn.close()
        inputs: Dict[str, Dict[str, Any]] = {}
        for node_name, port_name, value_json in results:
            if node_name not in inputs:
                inputs[node_name] = {}
            inputs[node_name][port_name] = json.loads(value_json)
        return inputs

    def add_to_history(
        self,
        session_id: str,
        node_name: str,
        port_name: str,
        value: Any,
        source_input: Optional[str] = None,
    ) -> int:
        now = datetime.now().isoformat()
        value_json = json.dumps(value, default=str)
        source_json = json.dumps(source_input, default=str) if source_input else None
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO port_history 
               (session_id, node_name, port_name, value, source_input, created_at, selected) 
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (session_id, node_name, port_name, value_json, source_json, now),
        )
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return history_id

    def get_history(
        self, session_id: str, node_name: str, port_name: str
    ) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, value, source_input, created_at, selected 
               FROM port_history 
               WHERE session_id = ? AND node_name = ? AND port_name = ?
               ORDER BY created_at DESC""",
            (session_id, node_name, port_name),
        )
        results = cursor.fetchall()
        conn.close()
        history = []
        for row in results:
            history.append(
                {
                    "id": row[0],
                    "value": json.loads(row[1]),
                    "source_input": json.loads(row[2]) if row[2] else None,
                    "created_at": row[3],
                    "selected": bool(row[4]),
                }
            )
        return history

    def select_history_item(
        self, session_id: str, node_name: str, port_name: str, history_id: int
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE port_history SET selected = 0 
               WHERE session_id = ? AND node_name = ? AND port_name = ?""",
            (session_id, node_name, port_name),
        )
        cursor.execute(
            "UPDATE port_history SET selected = 1 WHERE id = ?",
            (history_id,),
        )
        conn.commit()
        conn.close()

    def get_selected_history(
        self, session_id: str, node_name: str, port_name: str
    ) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, value, source_input, created_at 
               FROM port_history 
               WHERE session_id = ? AND node_name = ? AND port_name = ? AND selected = 1""",
            (session_id, node_name, port_name),
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                "id": result[0],
                "value": json.loads(result[1]),
                "source_input": json.loads(result[2]) if result[2] else None,
                "created_at": result[3],
            }
        return None

    def save_result(self, session_id: str, node_name: str, result: Any):
        now = datetime.now().isoformat()
        result_json = json.dumps(result, default=str)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO node_results (session_id, node_name, result, created_at) VALUES (?, ?, ?, ?)",
            (session_id, node_name, result_json, now),
        )
        conn.commit()
        conn.close()

    def get_latest_result(self, session_id: str, node_name: str) -> Optional[Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT result FROM node_results 
               WHERE session_id = ? AND node_name = ? 
               ORDER BY created_at DESC LIMIT 1""",
            (session_id, node_name),
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            return json.loads(result[0])
        return None

    def get_all_results(self, session_id: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT node_name, result FROM node_results 
               WHERE session_id = ? 
               ORDER BY created_at DESC""",
            (session_id,),
        )
        results = cursor.fetchall()
        conn.close()
        latest: Dict[str, Any] = {}
        for node_name, result_json in results:
            if node_name not in latest:
                latest[node_name] = json.loads(result_json)
        return latest

    def get_all_history(
        self, session_id: str
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT node_name, port_name, id, value, source_input, created_at, selected 
               FROM port_history 
               WHERE session_id = ?
               ORDER BY created_at DESC""",
            (session_id,),
        )
        results = cursor.fetchall()
        conn.close()
        history: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        for row in results:
            node_name, port_name = row[0], row[1]
            if node_name not in history:
                history[node_name] = {}
            if port_name not in history[node_name]:
                history[node_name][port_name] = []
            history[node_name][port_name].append(
                {
                    "id": row[2],
                    "value": json.loads(row[3]),
                    "source_input": json.loads(row[4]) if row[4] else None,
                    "created_at": row[5],
                    "selected": bool(row[6]),
                }
            )
        return history
