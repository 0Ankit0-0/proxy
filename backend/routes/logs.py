from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pathlib import Path
import os
import shutil
from config import TEMP_DIR, LOGS_DIR
from pydantic import BaseModel

from services.parser_service import LogParser
from services.collector_service import LogCollector
from services.storage_service import StorageService

class UploadResponse(BaseModel):
    status: str
    message: str
    filename: str

router = APIRouter()

# Ensure directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_logs(file: UploadFile = File(...)):
    """
    Upload a log file for offline analysis
    Supports: .log, .txt, .evtx, .json, .csv, .gz
    """
    # Validate file extension
    allowed_extensions = {'.log', '.txt', '.evtx', '.json', '.csv', '.evt', '.gz'}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not supported"
        )

    try:
        temp_path = TEMP_DIR / file.filename

        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        return UploadResponse(
            status="success",
            message=f"File uploaded successfully",
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/collect/local")
async def collect_local_logs(background_tasks: BackgroundTasks):
    """
    Collect logs from the local system (cross-platform)
    Supports: Windows, Linux, macOS
    """
    import platform
    
    try:
        collector = LogCollector()
        
        # Detect OS and collect appropriate logs
        system = platform.system()
        
        if system == "Linux":
            collected_files = collector.collect_linux_logs()
        elif system == "Darwin":  # macOS
            collected_files = collector.collect_macos_logs()
        elif system == "Windows":
            collected_files = collector.collect_windows_logs()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported operating system: {system}"
            )
        
        # Copy to TEMP_DIR for processing
        processed_files = []
        for file in collected_files:
            dest = TEMP_DIR / file.name
            shutil.copy2(file, dest)
            processed_files.append(str(dest))
        
        return {
            "status": "success",
            "message": f"Collected logs from {system}",
            "system": system,
            "files_collected": len(processed_files),
            "files": processed_files[:10]  # Limit response size
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Local collection failed: {str(e)}"
        )


@router.post("/collect/directory")
async def collect_from_directory(directory_path: str):
    """
    Collect logs from a specific directory
    Useful for importing logs from USB drives or network shares
    """
    try:
        source_dir = Path(directory_path)
        
        if not source_dir.exists() or not source_dir.is_dir():
            raise HTTPException(status_code=400, detail="Invalid directory path")
        
        collector = LogCollector(logs_dir=source_dir)
        collected_files = collector.collect_local()
        
        return {
            "status": "success",
            "message": f"Collected logs from {directory_path}",
            "files_collected": len(collected_files),
            "files": [str(f) for f in collected_files[:10]]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Directory collection failed: {str(e)}"
        )


@router.post("/parse")
async def parse_uploaded_logs():
    """
    Parse all uploaded/collected logs in TEMP_DIR
    Converts raw logs to structured format
    """
    try:
        parsed_data = {}
        
        for file_path in TEMP_DIR.iterdir():
            if file_path.is_dir():
                continue
            
            try:
                with open(file_path, 'r', errors="ignore") as f:
                    content = f.read()
                
                lines = content.splitlines()
                
                # Try different parsers
                try:
                    df = LogParser.parse_syslog_lines(lines)
                    parser_type = "syslog"
                except Exception:
                    try:
                        df = LogParser.parse_json_logs(lines)
                        parser_type = "json"
                    except Exception:
                        df = LogParser.parse_generic_text(lines)
                        parser_type = "generic"
                
                parsed_data[file_path.name] = {
                    "rows": df.shape[0],
                    "parser": parser_type,
                    "columns": df.columns
                }
                
            except Exception as e:
                parsed_data[file_path.name] = {
                    "error": str(e)
                }
        
        return {
            "status": "success",
            "files_parsed": len(parsed_data),
            "details": parsed_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


@router.post("/store")
async def store_parsed_logs():
    """
    Store parsed logs into DuckDB
    Creates unified schema for analysis
    """
    try:
        stored_files = []
        total_rows = 0
        
        for file_path in TEMP_DIR.iterdir():
            if file_path.is_dir():
                continue
            
            try:
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read()
                
                lines = content.splitlines()
                
                # Parse with fallback logic
                try:
                    df = LogParser.parse_syslog_lines(lines)
                except Exception:
                    try:
                        df = LogParser.parse_json_logs(lines)
                    except Exception:
                        df = LogParser.parse_generic_text(lines)
                
                # Store in DuckDB
                StorageService.insert_polars_df(df)
                
                stored_files.append(file_path.name)
                total_rows += df.shape[0]
                
            except Exception as e:
                print(f"Error storing {file_path.name}: {e}")
        
        return {
            "status": "success",
            "files_stored": len(stored_files),
            "total_rows": total_rows,
            "files": stored_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")


@router.get("/query")
async def query_logs(query: str):
    """
    Execute SQL query on stored logs
    Example: SELECT * FROM logs WHERE is_anomaly = TRUE LIMIT 10
    """
    try:
        # Security: Basic SQL injection prevention
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE']
        if any(keyword in query.upper() for keyword in dangerous_keywords):
            raise HTTPException(status_code=400, detail="Unsafe query detected")
        
        result = StorageService.query_logs(query)
        
        return {
            "status": "success",
            "rows": len(result),
            "data": result[:100]  # Limit response size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.delete("/clear")
async def clear_temp_logs():
    """
    Clear all temporary log files
    Useful for cleanup after analysis
    """
    try:
        deleted_count = 0
        
        for file_path in TEMP_DIR.iterdir():
            if file_path.is_file():
                file_path.unlink()
                deleted_count += 1
        
        return {
            "status": "success",
            "message": f"Cleared {deleted_count} temporary files"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/status")
async def get_collection_status():
    """
    Get current status of log collection and storage
    """
    try:
        import platform
        
        # Count files in TEMP_DIR
        temp_files = [f for f in TEMP_DIR.iterdir() if f.is_file()]
        temp_size = sum(f.stat().st_size for f in temp_files)
        
        # Query database stats
        with StorageService.get_connection() as conn:
            stats = conn.execute("""
                SELECT
                    COUNT(*) as total_logs,
                    COUNT(DISTINCT host) as unique_hosts,
                    COUNT(CASE WHEN is_anomaly = TRUE THEN 1 END) as anomalies
                FROM logs
            """).fetchone()
        
        return {
            "status": "operational",
            "system": platform.system(),
            "temp_storage": {
                "files": len(temp_files),
                "size_mb": round(temp_size / (1024 * 1024), 2)
            },
            "database": {
                "total_logs": stats[0],
                "unique_hosts": stats[1],
                "anomalies": stats[2]
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }