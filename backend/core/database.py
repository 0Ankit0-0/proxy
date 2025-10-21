import duckdb
from config import DB_PATH

def get_db_collection():
    """Initialize DuckDB with complete schema"""
    conn = duckdb.connect(str(DB_PATH))

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


