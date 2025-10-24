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
            is_anomaly BOOLEAN DEFAULT FALSE,
            severity VARCHAR DEFAULT 'low',
            detections TEXT,
            ttp_tags TEXT,
            content_hash VARCHAR
        );
    """)

    # Create indexes for performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_anomaly ON logs(is_anomaly);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_host ON logs(host);")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_content_hash ON logs(content_hash);")

    return conn


