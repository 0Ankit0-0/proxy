import duckdb
from config import DB_PATH
from core.database import get_db_collection
import polars as pl
from contextlib import contextmanager

class StorageService:
    """
    Service for storing and querying logs in DuckDB.
    """

    @staticmethod
    @contextmanager
    def get_connection():
        """Context manager for database connections"""
        conn = get_db_collection()
        try:
            yield conn
        finally:
            # DuckDB connections should be explicitly managed
            pass  # Add cleanup if needed

    @staticmethod
    def insert_polars_df(df, table_name: str = "logs", batch_size: int = 1000):
        """Optimized batch insertion"""
        with StorageService.get_connection() as conn:
            try:
                # Add missing columns if they don't exist
                if 'source_file' not in df.columns:
                    df = df.with_columns(pl.lit('unknown').alias('source_file'))
                if 'anomaly_score' not in df.columns:
                    df = df.with_columns(pl.lit(0.0).alias('anomaly_score'))

                # Batch insert for performance
                for i in range(0, len(df), batch_size):
                    batch = df.slice(i, min(batch_size, len(df) - i))
                    conn.register("batch_df", batch.to_pandas())
                    conn.execute(f"INSERT INTO {table_name} SELECT * FROM batch_df")

                conn.execute("CHECKPOINT")  # Force write to disk

            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    def query_logs(query: str):
        """
        Execute a SQL query on the logs table and return results.
        """
        with StorageService.get_connection() as conn:
            try:
                result = conn.execute(query).fetchall()
                return result
            except Exception as e:
                conn.rollback()
                raise e
