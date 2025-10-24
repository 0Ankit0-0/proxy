import duckdb
import os
from config import DB_PATH

def get_db_collection():
    """
    Initialize DuckDB with complete schema.
    If the PYTEST_RUNNING environment variable is set, it uses an in-memory database.
    """
    db_path = ":memory:" if os.getenv("PYTEST_RUNNING") else str(DB_PATH)
    conn = duckdb.connect(db_path)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP,
            host VARCHAR,
            process VARCHAR,
            pid BIGINT,
            message TEXT,
            raw TEXT,
            source_file VARCHAR DEFAULT 'unknown',
            anomaly_score DOUBLE DEFAULT 0.0,
            is_anomaly BOOLEAN DEFAULT FALSE
        );
    """)

    # Create indexes for performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_anomaly ON logs(is_anomaly);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_host ON logs(host);")

    return conn


