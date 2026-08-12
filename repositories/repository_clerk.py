import sqlite3
from pathlib import Path
from typing import Any, Optional


class RepositoryClerk:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS lost_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    location_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    FOREIGN KEY(student_id) REFERENCES students(id),
                    FOREIGN KEY(item_id) REFERENCES items(id),
                    FOREIGN KEY(location_id) REFERENCES locations(id)
                );

                CREATE TABLE IF NOT EXISTS found_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    location_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    FOREIGN KEY(student_id) REFERENCES students(id),
                    FOREIGN KEY(item_id) REFERENCES items(id),
                    FOREIGN KEY(location_id) REFERENCES locations(id)
                );

                CREATE TABLE IF NOT EXISTS claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    found_report_id INTEGER NOT NULL,
                    identifying_information TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    FOREIGN KEY(student_id) REFERENCES students(id),
                    FOREIGN KEY(found_report_id) REFERENCES found_reports(id)
                );

                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(student_id) REFERENCES students(id)
                );
                """
            )

    def create_student(self, name: str, contact: str) -> int:
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO students (name, contact) VALUES (?, ?)",
                (name, contact),
            )
            return cursor.lastrowid

    def create_item(self, description: str, category: str) -> int:
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO items (description, category) VALUES (?, ?)",
                (description, category),
            )
            return cursor.lastrowid

    def create_location(self, description: str) -> int:
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO locations (description) VALUES (?)",
                (description,),
            )
            return cursor.lastrowid

    def create_lost_report(
        self, student_id: int, item_id: int, location_id: int
    ) -> int:
        with self._connect() as db:
            cursor = db.execute(
                """
                INSERT INTO lost_reports
                    (student_id, item_id, location_id)
                VALUES (?, ?, ?)
                """,
                (student_id, item_id, location_id),
            )
            return cursor.lastrowid

    def create_found_report(
        self, student_id: int, item_id: int, location_id: int
    ) -> int:
        with self._connect() as db:
            cursor = db.execute(
                """
                INSERT INTO found_reports
                    (student_id, item_id, location_id)
                VALUES (?, ?, ?)
                """,
                (student_id, item_id, location_id),
            )
            return cursor.lastrowid

    def search_found_reports(
        self,
        description: str = "",
        category: str = "",
        location: str = "",
    ) -> list[sqlite3.Row]:
        conditions = ["fr.status = 'open'"]
        parameters: list[Any] = []

        if description:
            conditions.append("LOWER(i.description) LIKE ?")
            parameters.append(f"%{description.lower()}%")

        if category:
            conditions.append("LOWER(i.category) = ?")
            parameters.append(category.lower())

        if location:
            conditions.append("LOWER(l.description) LIKE ?")
            parameters.append(f"%{location.lower()}%")

        query = f"""
            SELECT
                fr.id AS found_report_id,
                fr.status,
                i.description,
                i.category,
                l.description AS location,
                s.name AS finder_name
            FROM found_reports fr
            JOIN items i ON i.id = fr.item_id
            JOIN locations l ON l.id = fr.location_id
            JOIN students s ON s.id = fr.student_id
            WHERE {' AND '.join(conditions)}
            ORDER BY fr.id DESC
        """

        with self._connect() as db:
            return db.execute(query, parameters).fetchall()

    def get_found_report(self, found_report_id: int) -> Optional[sqlite3.Row]:
        with self._connect() as db:
            return db.execute(
                """
                SELECT
                    fr.id AS found_report_id,
                    fr.student_id AS finder_id,
                    fr.status,
                    i.description,
                    i.category,
                    l.description AS location,
                    s.name AS finder_name,
                    s.contact AS finder_contact
                FROM found_reports fr
                JOIN items i ON i.id = fr.item_id
                JOIN locations l ON l.id = fr.location_id
                JOIN students s ON s.id = fr.student_id
                WHERE fr.id = ?
                """,
                (found_report_id,),
            ).fetchone()

    def get_lost_reports_for_matching(
        self, description: str, category: str, location: str
    ) -> list[sqlite3.Row]:
        conditions = ["lr.status = 'open'"]
        parameters: list[Any] = []

        if description:
            conditions.append("LOWER(i.description) LIKE ?")
            parameters.append(f"%{description.lower()}%")

        if category:
            conditions.append("LOWER(i.category) = ?")
            parameters.append(category.lower())

        if location:
            conditions.append("LOWER(l.description) LIKE ?")
            parameters.append(f"%{location.lower()}%")

        query = f"""
            SELECT
                lr.id,
                lr.student_id,
                i.description,
                i.category,
                l.description AS location
            FROM lost_reports lr
            JOIN items i ON i.id = lr.item_id
            JOIN locations l ON l.id = lr.location_id
            WHERE {' AND '.join(conditions)}
        """

        with self._connect() as db:
            return db.execute(query, parameters).fetchall()

    def create_claim(
        self,
        student_id: int,
        found_report_id: int,
        identifying_information: str,
    ) -> int:
        with self._connect() as db:
            cursor = db.execute(
                """
                INSERT INTO claims
                    (student_id, found_report_id, identifying_information)
                VALUES (?, ?, ?)
                """,
                (student_id, found_report_id, identifying_information),
            )
            return cursor.lastrowid

    def create_notification(self, student_id: int, message: str) -> int:
        with self._connect() as db:
            cursor = db.execute(
                """
                INSERT INTO notifications (student_id, message)
                VALUES (?, ?)
                """,
                (student_id, message),
            )
            return cursor.lastrowid

    def get_notifications(self, student_id: int) -> list[sqlite3.Row]:
        with self._connect() as db:
            return db.execute(
                """
                SELECT id, message, is_read
                FROM notifications
                WHERE student_id = ?
                ORDER BY id DESC
                """,
                (student_id,),
            ).fetchall()

    def mark_notification_read(self, notification_id: int) -> None:
        with self._connect() as db:
            db.execute(
                "UPDATE notifications SET is_read = 1 WHERE id = ?",
                (notification_id,),
            )

    def update_claim_status(self, claim_id: int, status: str) -> None:
        with self._connect() as db:
            db.execute(
                "UPDATE claims SET status = ? WHERE id = ?",
                (status, claim_id),
            )
