import duckdb
from config import DB_PATH
from core.database import get_db_collection

class StorageService:
    """
    Service for storing and querying logs in DuckDB.
    """

    @staticmethod
    def insert_polars_df(df, table_name: str = "logs"):
        """
        Insert a Polars DataFrame into DuckDB.
        """
        conn = get_db_collection()
        try:
            # Convert Polars DataFrame to DuckDB table
            conn.register("temp_df", df.to_pandas())
            conn.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")
        finally:
            conn.close()

    @staticmethod
    def query_logs(query: str):
        """
        Execute a SQL query on the logs table and return results.
        """
        conn = get_db_collection()
        try:
            result = conn.execute(query).fetchall()
            return result
        finally:
            conn.close()
