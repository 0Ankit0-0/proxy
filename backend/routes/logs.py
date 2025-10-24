from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, status, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import os
import shutil
import platform
from typing import List, Optional
from pydantic import BaseModel, Field

from config import TEMP_DIR, LOGS_DIR
from services.parser_service import LogParser
from services.collector_service import LogCollector
from services.storage_service import StorageService

router = APIRouter()

# Ensure directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================ 
# 📂 Upload Endpoint
# ============================================================ 

class UploadResponse(BaseModel):
    status: str
    message: str
    filename: str


@router.post("/upload", response_model=UploadResponse)
async def upload_logs(file: UploadFile = File(...)):
    """
    Upload a log file for offline analysis
    Supports: .log, .txt, .evtx, .json, .csv, .gz
    """
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
            message="File uploaded successfully",
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


# ============================================================ 
# 🧠 Local and Directory Collection
# ============================================================ 

@router.post("/collect")
async def collect_local_logs(background_tasks: BackgroundTasks):
    """
    Collect logs from the local system (cross-platform)
    Supports: Windows, Linux, macOS
    """
    try:
        collector = LogCollector(temp_dir=TEMP_DIR)
        system = platform.system()

        if system == "Linux":
            collected_files = collector.collect_linux_logs()
        elif system == "Darwin":
            collected_files = collector.collect_macos_logs()
        elif system == "Windows":
            collected_files = collector.collect_windows_logs()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported operating system: {system}"
            )

        processed_files = []
        for file in collected_files:
            dest = TEMP_DIR / file.name
            shutil.copy2(file, dest)
            processed_files.append(str(dest))

        return {
            "status": "Logs collected successfully",
            "collected_files": processed_files[:10]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Local collection failed: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Directory collection failed: {str(e)}")


# ============================================================ 
# 🌐 Remote Collection (SSH / WinRM / Network Share)
# ============================================================ 

class SSHCollectionRequest(BaseModel):
    host: str = Field(..., description="Remote host IP/hostname")
    username: str
    password: str
    remote_paths: Optional[List[str]] = None


class WinRMCollectionRequest(BaseModel):
    host: str = Field(..., description="Remote Windows host IP/hostname")
    username: str
    password: str
    remote_paths: Optional[List[str]] = None


class NetworkShareRequest(BaseModel):
    network_path: str = Field(..., description="UNC path like \\server\share")
    username: Optional[str] = None
    password: Optional[str] = None


@router.post("/collect/ssh")
async def collect_from_ssh(request: SSHCollectionRequest):
    """
    Collect logs from remote Linux/Unix server via SSH
    Requires paramiko library
    """
    try:
        collector = LogCollector(temp_dir=TEMP_DIR)
        collected_files = collector.collect_remote_ssh(
            host=request.host,
            username=request.username,
            password=request.password,
            remote_paths=request.remote_paths
        )

        return {
            "status": "success",
            "message": f"Collected logs from {request.host} via SSH",
            "files_collected": len(collected_files),
            "files": [str(f) for f in collected_files]
        }

    except ImportError:
        raise HTTPException(
            status_code=400,
            detail="paramiko not installed. Install with: pip install paramiko"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SSH collection failed: {str(e)}")


@router.post("/collect/winrm")
async def collect_from_winrm(request: WinRMCollectionRequest):
    """
    Collect logs from remote Windows server via WinRM
    Requires pywinrm library
    """
    try:
        collector = LogCollector(temp_dir=TEMP_DIR)
        collected_files = collector.collect_remote_winrm(
            host=request.host,
            username=request.username,
            password=request.password,
            remote_paths=request.remote_paths
        )

        return {
            "status": "success",
            "message": f"Collected logs from {request.host} via WinRM",
            "files_collected": len(collected_files),
            "files": [str(f) for f in collected_files]
        }

    except ImportError:
        raise HTTPException(
            status_code=400,
            detail="pywinrm not installed. Install with: pip install pywinrm"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WinRM collection failed: {str(e)}")


@router.post("/collect/network")
async def collect_from_network_share(request: NetworkShareRequest):
    """
    Collect logs from Windows network share (SMB/CIFS)
    Windows only - uses net use command
    """
    try:
        if platform.system() != "Windows":
            raise HTTPException(
                status_code=400,
                detail="Network share collection only supported on Windows"
            )

        collector = LogCollector(temp_dir=TEMP_DIR)
        collected_files = collector.collect_network_logs(
            network_path=request.network_path,
            username=request.username,
            password=request.password
        )

        return {
            "status": "success",
            "message": "Collected logs from network share",
            "files_collected": len(collected_files),
            "files": [str(f) for f in collected_files]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network share collection failed: {str(e)}")


# ============================================================ 
# 🧩 Parsing / Storage / Query / Cleanup
# ============================================================ 

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
                parsed_data[file_path.name] = {"error": str(e)}

        return {
            "status": "Logs parsed successfully",
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

            with open(file_path, "r", errors="ignore") as f:
                content = f.read()
            lines = content.splitlines()

            try:
                df = LogParser.parse_syslog_lines(lines)
            except Exception:
                try:
                    df = LogParser.parse_json_logs(lines)
                except Exception:
                    df = LogParser.parse_generic_text(lines)

            StorageService.insert_polars_df(df)
            stored_files.append(file_path.name)
            total_rows += df.shape[0]

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
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE']
        if any(keyword in query.upper() for keyword in dangerous_keywords):
            raise HTTPException(status_code=400, detail="Unsafe query detected")

        result = StorageService.query_logs(query)
        return {"status": "success", "rows": len(result), "data": result[:100]}

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

        return {"status": "success", "message": f"Cleared {deleted_count} temporary files"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/status")
async def get_collection_status():
    """
    Get current status of log collection and storage
    """
    try:
        temp_files = [f for f in TEMP_DIR.iterdir() if f.is_file()]
        temp_size = sum(f.stat().st_size for f in temp_files)

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
        return {"status": "error", "message": str(e)}


# ============================================================ 
# 🔌 USB Collection
# ============================================================ 

@router.post("/collect/usb")
async def collect_from_usb(
    auto_detect: bool = Query(True, description="Auto-detect USB drives"),
    mount_point: Optional[str] = Query(None, description="Specific USB mount point")
):
    """
    Collect logs from USB/removable drives
    
    This endpoint supports true offline log collection:
    - Auto-detects mounted USB drives
    - Scans for .log, .evtx, .json files
    - Copies to temp storage for analysis
    
    Use cases:
    - Field analysts with USB-collected logs
    - Offline transfer from isolated systems
    - Manual log aggregation
    """
    try:
        collector = LogCollector(temp_dir=TEMP_DIR)
        
        mount = Path(mount_point) if mount_point else None
        collected_files = collector.collect_from_usb(
            auto_detect=auto_detect,
            mount_point=mount
        )
        
        return {
            "status": "success",
            "message": f"Collected logs from USB drive(s)",
            "files_collected": len(collected_files),
            "files": [str(f) for f in collected_files[:20]]  # First 20
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"USB collection failed: {str(e)}"
        )


@router.get("/collect/usb/detect")
async def detect_usb_drives():
    """
    Detect available USB/removable drives
    
    Returns list of mount points that can be used for log collection
    """
    try:
        collector = LogCollector()
        usb_drives = collector.detect_usb_drives()
        
        return {
            "status": "success",
            "drives_detected": len(usb_drives),
            "drives": [
                {
                    "mount_point": str(drive),
                    "name": drive.name,
                    "exists": drive.exists()
                }
                for drive in usb_drives
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"USB detection failed: {str(e)}"
        )