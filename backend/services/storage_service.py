import duckdb
from config import DB_PATH
from core.database import get_db_collection
import polars as pl
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class StorageService:
    """
    Service for storing and querying logs in DuckDB.
    Implements proper connection pooling and error handling.
    """
    
    _connection = None  # Singleton connection

    @staticmethod
    @contextmanager
    def get_connection():
        """Context manager for database connections with proper cleanup"""
        conn = None
        try:
            conn = get_db_collection()
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")

    @staticmethod
    def insert_polars_df(df: pl.DataFrame, table_name: str = "logs", batch_size: int = 1000):
        """
        Optimized batch insertion with proper error handling
        
        Args:
            df: Polars DataFrame with log data
            table_name: Target table name (default: 'logs')
            batch_size: Number of rows per batch (default: 1000)
        """
        with StorageService.get_connection() as conn:
            try:
                # Ensure required columns exist
                required_columns = {
                    'timestamp': pl.Datetime(time_unit='ms'),
                    'host': pl.Utf8,
                    'process': pl.Utf8,
                    'pid': pl.Int64,  # Keep as integer
                    'message': pl.Utf8,
                    'raw': pl.Utf8,
                    'source_file': pl.Utf8,
                    'anomaly_score': pl.Float64
                }
                
                # Add missing columns with default values
                for col_name, col_type in required_columns.items():
                    if col_name not in df.columns:
                        if col_name == 'source_file':
                            df = df.with_columns(pl.lit('unknown').alias(col_name))
                        elif col_name == 'anomaly_score':
                            df = df.with_columns(pl.lit(0.0).alias(col_name))
                        elif col_name in ['timestamp', 'host', 'process', 'pid', 'message', 'raw']:
                            df = df.with_columns(pl.lit(None).cast(col_type).alias(col_name))
                
                # Convert to pandas for DuckDB (more efficient than registering)
                df_pandas = df.to_pandas()
                
                # Batch insert for better performance
                total_rows = len(df_pandas)
                inserted_rows = 0
                
                for i in range(0, total_rows, batch_size):
                    batch = df_pandas.iloc[i:i + batch_size]
                    conn.register("batch_df", batch)
                    conn.execute(f"INSERT INTO {table_name} SELECT * FROM batch_df")
                    inserted_rows += len(batch)
                    logger.info(f"Inserted {inserted_rows}/{total_rows} rows")
                
                # Commit changes
                conn.execute("CHECKPOINT")
                logger.info(f"✅ Successfully stored {total_rows} rows in {table_name}")
                
                return total_rows

            except Exception as e:
                logger.error(f"❌ Insert failed: {e}")
                conn.rollback()
                raise

    @staticmethod
    def query_logs(query: str, params: tuple = None):
        """
        Execute a SQL query on the logs table and return results.
        
        Args:
            query: SQL query string
            params: Optional tuple of parameters for prepared statements
            
        Returns:
            List of tuples containing query results
        """
        with StorageService.get_connection() as conn:
            try:
                if params:
                    result = conn.execute(query, params).fetchall()
                else:
                    result = conn.execute(query).fetchall()
                return result
            except Exception as e:
                logger.error(f"❌ Query failed: {e}")
                raise
    
    @staticmethod
    def get_statistics():
        """Get database statistics"""
        with StorageService.get_connection() as conn:
            try:
                stats = conn.execute("""
                    SELECT
                        COUNT(*) as total_logs,
                        COUNT(DISTINCT host) as unique_hosts,
                        COUNT(CASE WHEN is_anomaly = TRUE THEN 1 END) as anomalies,
                        MIN(timestamp) as earliest_log,
                        MAX(timestamp) as latest_log,
                        AVG(anomaly_score) as avg_anomaly_score
                    FROM logs
                """).fetchone()
                
                return {
                    "total_logs": stats[0],
                    "unique_hosts": stats[1],
                    "anomalies": stats[2],
                    "earliest_log": stats[3],
                    "latest_log": stats[4],
                    "avg_anomaly_score": round(stats[5], 4) if stats[5] else 0.0
                }
            except Exception as e:
                logger.error(f"Error fetching statistics: {e}")
                return {}