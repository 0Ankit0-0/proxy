import duckdb
from config import DB_PATH

def get_db_collection():
    """Return a DuckDB connection (auto-) """
    conn = duckdb.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS logs (
            timestamp TIMESTAMP,
            host TEXT,
            process TEXT,
            pid BIGINT,
            message TEXT,
            raw TEXT,
            source_file TEXT,
            anomaly_score DOUBLE
        );
    """)
    return conn


