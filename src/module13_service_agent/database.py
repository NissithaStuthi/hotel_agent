"""Module 13: Local SQLite Database for Guest Service Requests

Provides local persistent storage for guest service tickets, status updates,
and audit logs.
"""

import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from contextlib import contextmanager
from src.config import DATA_DIR
from src.module13_service_agent.models import (
    ServiceRequest,
    ServiceCategory,
    ServicePriority,
    ServiceRequestStatus
)

DB_PATH = DATA_DIR / "service_requests.db"


class ServiceRequestDatabase:
    """Manages SQLite storage for hotel guest service tickets."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initializes database schema and indexes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS service_requests (
                    request_id TEXT PRIMARY KEY,
                    ticket_number TEXT UNIQUE NOT NULL,
                    room_number TEXT NOT NULL,
                    guest_name TEXT,
                    category TEXT NOT NULL,
                    requested_items TEXT,
                    notes TEXT,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    estimated_turnaround_minutes INTEGER NOT NULL,
                    estimated_completion_time TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_req_room ON service_requests(room_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_req_ticket ON service_requests(ticket_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_req_status ON service_requests(status)")
            conn.commit()

    def generate_ticket_number(self) -> str:
        """Generates sequential daily ticket code like REQ-20261017-001."""
        today_str = datetime.now().strftime("%Y%m%d")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM service_requests WHERE ticket_number LIKE ?",
                (f"REQ-{today_str}-%",)
            )
            count = cursor.fetchone()["count"]
            seq = count + 1
            return f"REQ-{today_str}-{seq:03d}"

    def create_request(
        self,
        room_number: str,
        category: ServiceCategory,
        requested_items: List[str],
        notes: str = "",
        guest_name: str = "Esteemed Guest",
        priority: ServicePriority = ServicePriority.NORMAL,
        estimated_turnaround_minutes: int = 15
    ) -> ServiceRequest:
        """Inserts a new guest service ticket."""
        now = datetime.now()
        comp_time = now + timedelta(minutes=estimated_turnaround_minutes)
        ticket_number = self.generate_ticket_number()
        request_id = str(uuid.uuid4())

        request = ServiceRequest(
            request_id=request_id,
            ticket_number=ticket_number,
            room_number=str(room_number).upper(),
            guest_name=guest_name,
            category=category,
            requested_items=requested_items,
            notes=notes,
            priority=priority,
            status=ServiceRequestStatus.PENDING,
            created_at=now.strftime("%Y-%m-%d %H:%M:%S"),
            estimated_turnaround_minutes=estimated_turnaround_minutes,
            estimated_completion_time=comp_time.strftime("%Y-%m-%d %H:%M:%S")
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO service_requests (
                    request_id, ticket_number, room_number, guest_name, category,
                    requested_items, notes, priority, status, created_at,
                    estimated_turnaround_minutes, estimated_completion_time, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.request_id,
                request.ticket_number,
                request.room_number,
                request.guest_name,
                request.category.value,
                json.dumps(request.requested_items),
                request.notes,
                request.priority.value,
                request.status.value,
                request.created_at,
                request.estimated_turnaround_minutes,
                request.estimated_completion_time,
                request.completed_at
            ))
            conn.commit()

        return request

    def get_request(self, ticket_or_id: str) -> Optional[ServiceRequest]:
        """Retrieves a request by ticket_number or request_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM service_requests WHERE ticket_number = ? OR request_id = ?",
                (ticket_or_id.upper(), ticket_or_id)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_model(row)

    def list_requests(
        self,
        room_number: Optional[str] = None,
        status: Optional[ServiceRequestStatus] = None,
        limit: int = 50
    ) -> List[ServiceRequest]:
        """Lists service requests with optional filters."""
        query = "SELECT * FROM service_requests WHERE 1=1"
        params: List[Any] = []

        if room_number:
            query += " AND room_number = ?"
            params.append(str(room_number).upper())
        if status:
            query += " AND status = ?"
            params.append(status.value)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_model(r) for r in rows]

    def update_status(self, ticket_or_id: str, new_status: ServiceRequestStatus) -> bool:
        """Updates the status of a service ticket."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        completed_at = now_str if new_status == ServiceRequestStatus.COMPLETED else None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE service_requests 
                SET status = ?, completed_at = COALESCE(?, completed_at)
                WHERE ticket_number = ? OR request_id = ?
            """, (new_status.value, completed_at, ticket_or_id.upper(), ticket_or_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_statistics(self) -> Dict[str, Any]:
        """Calculates service request metrics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM service_requests")
            total = cursor.fetchone()["total"]

            cursor.execute("SELECT status, COUNT(*) as count FROM service_requests GROUP BY status")
            by_status = {row["status"]: row["count"] for row in cursor.fetchall()}

            cursor.execute("SELECT category, COUNT(*) as count FROM service_requests GROUP BY category")
            by_category = {row["category"]: row["count"] for row in cursor.fetchall()}

            return {
                "total_requests": total,
                "by_status": by_status,
                "by_category": by_category
            }

    def _row_to_model(self, row: sqlite3.Row) -> ServiceRequest:
        items = json.loads(row["requested_items"]) if row["requested_items"] else []
        return ServiceRequest(
            request_id=row["request_id"],
            ticket_number=row["ticket_number"],
            room_number=row["room_number"],
            guest_name=row["guest_name"],
            category=ServiceCategory(row["category"]),
            requested_items=items,
            notes=row["notes"],
            priority=ServicePriority(row["priority"]),
            status=ServiceRequestStatus(row["status"]),
            created_at=row["created_at"],
            estimated_turnaround_minutes=row["estimated_turnaround_minutes"],
            estimated_completion_time=row["estimated_completion_time"],
            completed_at=row["completed_at"]
        )
