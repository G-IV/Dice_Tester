"""
I basically let the VSCode AI write this section - I'm curious if I could have saved hours and hours by offloading this work.
"""

# Database support imports
from datetime import datetime
import sqlite3

# Parallelism support imports
import threading
import queue

# Datatype support imports
from pathlib import Path

# Project module imports
from Scripts.Modules.queue_data import QueueData, Command as QuCmd

DBPath = Path("/Users/georgeburrows/Documents/Desktop/Projects/Die Tester/Dice_Tester/Scripts/Modules/Database/dice.db")

class DBManager:
    def __init__(self, dice_id: str = None, logging=False):
        """Initialize database manager state."""
        self.dice_id = dice_id
        self.db_path = DBPath
        self.logging = logging
        self._write_queue = queue.Queue()
        self._writer_thread = None
        self.initialize_database()

    def initialize_database(self):
        '''Initialize the database and create necessary tables if they don't exist.
        
        dice_id: This should be applied to each tested die
        timestamp: When the test was conducted
        motor_position: In case we want to analyze results based on motor position
        dice_result: The number on the top face of the die
        image: path to the image captured when the dice came to a stop
        
        The primary key is a combination of dice_id and timestamp to ensure uniqueness.
        '''
        if self.logging:
            print("database.py initialize_database() called.")

        conn, cursor = self.open_connection()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS test_results (
                dice_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                dice_sides INTEGER,
                dice_result INTEGER NOT NULL,
                image TEXT NOT NULL,
                PRIMARY KEY (dice_id, timestamp)
            )
            '''
        )

        cursor.execute("PRAGMA table_info(test_results)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        if 'dice_sides' not in existing_columns:
            cursor.execute('ALTER TABLE test_results ADD COLUMN dice_sides INTEGER')

        conn.commit()
        self.close_connection(conn)
        if self.logging:
            print("  -> Database initialized and tables created if they didn't exist.")

    def open_connection(self):
        """
        Open a connection to the database.
        Returns a (connection, cursor) tuple for executing SQL commands.
        """
        if self.logging:
            print("database.py open_connection() called.")

        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn, conn.cursor()

    def close_connection(self, conn):
        """Close a provided sqlite connection."""
        if self.logging:
            print("database.py close_connection() called.")

        if conn:
            conn.close()
            if self.logging:
                print("  -> Database connection closed.")

    def start_writer(self):
        """Start a dedicated writer thread if it is not already running."""
        if self._writer_thread and self._writer_thread.is_alive():
            return

        self._writer_thread = threading.Thread(
            target=self._writer_loop,
            name="sqlite-writer",
            daemon=True,
        )
        self._writer_thread.start()
        if self.logging:
            print("  -> Database writer thread started.")

    def stop_writer(self):
        """Stop the dedicated writer thread and wait for it to shut down."""
        if not self._writer_thread or not self._writer_thread.is_alive():
            return

        self._write_queue.put(QueueData(cmd=QuCmd.DB_STOP_WRITER, data=None))
        self._writer_thread.join()
        self._writer_thread = None
        if self.logging:
            print("  -> Database writer thread stopped.")

    def _queue_db_command(self, cmd, data=None):
        """Queue a database command for serialized execution."""
        self.start_writer()
        self._write_queue.put(QueueData(cmd=cmd, data=data))

    def _writer_loop(self):
        """Continuously process database commands on a single connection."""
        conn, cursor = self.open_connection()
        try:
            while True:
                item = self._write_queue.get()
                try:
                    if item.cmd == QuCmd.DB_STOP_WRITER:
                        return

                    if item.cmd == QuCmd.DB_EXECUTE_SQL:
                        payload = item.data or {}
                        cursor.execute(payload["sql"], payload.get("params", ()))
                        conn.commit()
                        continue

                    if item.cmd == QuCmd.DB_CLEAR_ALL_DATA:
                        cursor.execute("DELETE FROM test_results")
                        conn.commit()
                        continue

                    if item.cmd == QuCmd.DB_WRITE_TEST_RESULT:
                        payload = item.data or {}
                        dice_id = str(payload["dice_id"])
                        dice_sides = payload.get("dice_sides")
                        dice_result = int(payload["dice_result"])
                        image_path = str(payload["image_path"])
                        timestamp = payload.get("timestamp") or datetime.now().isoformat(timespec="milliseconds")

                        cursor.execute(
                            """
                            INSERT INTO test_results (dice_id, timestamp, dice_sides, dice_result, image)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (str(dice_id), timestamp, dice_sides, dice_result, image_path),
                        )
                        conn.commit()
                        continue

                    raise ValueError(f"Unsupported database command: {item.cmd}")
                finally:
                    self._write_queue.task_done()
        finally:
            self.close_connection(conn)

    def enqueue_write(self, sql, params=()):
        """Queue a raw SQL write statement for serialized execution."""
        self._queue_db_command(
            QuCmd.DB_EXECUTE_SQL,
            {
                "sql": sql,
                "params": params,
            },
        )

    def wait_for_writes(self):
        """Block until all queued writes have been committed."""
        self._write_queue.join()

    def execute_read_one(self, sql, params=()):
        """Execute a read query using a short-lived read connection."""
        conn, cursor = self.open_connection()
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        finally:
            self.close_connection(conn)

    def generate_id(self):
        """Set self.dice_id to the next numeric ID as a string.

        The next ID is calculated as max(existing numeric IDs) + 1.
        """
        if self.logging:
            print("database.py generate_id() called.")
        conn, cursor = self.open_connection()
        try:
            cursor.execute(
                """
                SELECT CAST(COALESCE(MAX(CAST(dice_id AS INTEGER)), 0) + 1 AS TEXT) AS next_dice_id
                    FROM test_results
                    WHERE dice_id <> ''
                    AND dice_id NOT GLOB '*[^0-9]*'
                """
            )
            result = cursor.fetchone()
        finally:
            self.close_connection(conn)

        if result[0] is not None:
            self.dice_id = result[0]
        else:
            self.dice_id = "1"

        if self.logging:
            print(f"  -> Generated new dice ID: {self.dice_id}")

    def write_test_result(self, dice_result: str, image_path: str, dice_sides: int | None = None, wait=False):
        """Write a new test result row using string inputs.

        Args:
            dice_result: Numeric face value as a string.
            image_path: Path to the captured image as a string.
            dice_sides: Number of sides on the die, if known.
            wait: Whether to block until the queued write is committed.
        """
        if self.logging:
            print("database.py write_test_result() called.")

        if not self.dice_id:
            self.generate_id()

        self._queue_db_command(
            QuCmd.DB_WRITE_TEST_RESULT,
            {
                "dice_id": self.dice_id,
                "dice_sides": dice_sides,
                "dice_result": dice_result,
                "image_path": image_path,
                "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            },
        )
        if wait:
            self.wait_for_writes()

        if self.logging:
            print(
                f"  -> Queued result write: dice_id={self.dice_id}, "
                f"dice_result={dice_result}, image={image_path}"
            )

    def list_dice_ids(self):
        """Return all stored dice IDs in ascending numeric order where possible."""
        conn, cursor = self.open_connection()
        try:
            cursor.execute(
                """
                SELECT DISTINCT dice_id
                FROM test_results
                ORDER BY
                    CASE WHEN dice_id GLOB '[0-9]*' THEN CAST(dice_id AS INTEGER) END,
                    dice_id
                """
            )
            return [row[0] for row in cursor.fetchall()]
        finally:
            self.close_connection(conn)

    def read_all_results(self):
        """Return all test result rows.

        Returns a list of dicts with keys: dice_id, timestamp, dice_sides, dice_result, image.
        """
        rows = []
        conn, cursor = self.open_connection()
        try:
            cursor.execute(
                """
                SELECT dice_id, timestamp, dice_sides, dice_result, image
                FROM test_results
                ORDER BY dice_id, timestamp
                """
            )
            for row in cursor.fetchall():
                rows.append({
                    "dice_id": row[0],
                    "timestamp": row[1],
                    "dice_sides": row[2],
                    "dice_result": row[3],
                    "image": row[4],
                })
        finally:
            self.close_connection(conn)

        return rows

    def update_image_path(self, dice_id: str, timestamp: str, image_path: str, wait=False):
        """Update the stored image path for an existing test result row."""
        self._queue_db_command(
            QuCmd.DB_EXECUTE_SQL,
            {
                "sql": """
                    UPDATE test_results
                    SET image = ?
                    WHERE dice_id = ? AND timestamp = ?
                """,
                "params": (str(image_path), str(dice_id), str(timestamp)),
            },
        )
        if wait:
            self.wait_for_writes()

    def delete_result(self, dice_id: str, timestamp: str, wait=False):
        """Delete a test result row identified by dice_id and timestamp."""
        self._queue_db_command(
            QuCmd.DB_EXECUTE_SQL,
            {
                "sql": """
                    DELETE FROM test_results
                    WHERE dice_id = ? AND timestamp = ?
                """,
                "params": (str(dice_id), str(timestamp)),
            },
        )
        if wait:
            self.wait_for_writes()

    def read_results_for_die(self, dice_id: str):
        """Return all test result rows for a given dice_id.

        Returns a list of dicts with keys: dice_id, timestamp, dice_sides, dice_result, image.
        """
        rows = []
        conn, cursor = self.open_connection()
        try:
            cursor.execute(
                """
                SELECT dice_id, timestamp, dice_sides, dice_result, image
                FROM test_results
                WHERE dice_id = ?
                ORDER BY timestamp
                """,
                (str(dice_id),),
            )
            for row in cursor.fetchall():
                rows.append({
                    "dice_id": row[0],
                    "timestamp": row[1],
                    "dice_sides": row[2],
                    "dice_result": row[3],
                    "image": row[4],
                })
        finally:
            self.close_connection(conn)

        if self.logging:
            print(f"  -> Read {len(rows)} result(s) for dice_id={dice_id}")
        return rows

    def clear_all_data(self):
        """
        Clear all data from the test_results table in the database.
        """
        if self.logging:
            print("database.py clear_all_data() called.")

        self._queue_db_command(QuCmd.DB_CLEAR_ALL_DATA, None)
        self.wait_for_writes()

        if self.logging:
            print("  -> All data cleared from the database.")