import sqlite3   # Built-in Python database (zero setup required)
import os        # For finding the folder path
import time

# storing the db file in same folder as the script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "incidents.db")

#stp 2 db helper function

def get_db():
    """Opens a connection to SQLite and allows reading columns by name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # let us use row['column name'] like a dir
    return conn



def init_db():
    """creates the 'incidents' table if it doesn't exist yet."""
    conn = get_db()
    cursor = conn.cursor()
    # table columns = id, time, problem name, detection second, recovery sec , action taken , status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            problem_type TEXT NOT NULL,
            detection_time REAL NOT NULL,
            recovery_time REAL NOT NULL,
            action_taken TEXT NOT NULL,
            status TEXT NOT NULL
            )
""")
    conn.commit()
    conn.close()


def log_incident(problem_type, detection_time, recovery_time, action_taken, status="RESOLVED"):
    """Inserts a new incident record into the db."""
    conn = get_db()
    cursor = conn.cursor()
    now_str = time.strftime("%H:%M:%S")  # Current time (HH:MM:SS)
    cursor.execute("""
        INSERT INTO incidents (timestamp, problem_type, detection_time, recovery_time, action_taken, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (now_str, problem_type, round(detection_time, 2), round(recovery_time, 2), action_taken, status))
    conn.commit()
    conn.close()


def get_recent_incidents(limit=10):
    """Fetches the latest incidents to display on the dashboard table."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
def get_summary_metrics():
    """Calculates total recovered incidents and average recovery time."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(recovery_time) FROM incidents WHERE status = 'RESOLVED'")
    total_recovered, avg_recovery = cursor.fetchone()
    conn.close()
    return {
        "total_recovered": total_recovered or 0,
        "avg_recovery_time": round(avg_recovery or 0, 2)
    }
# Automatically initialize db when this file is loadedz
init_db()