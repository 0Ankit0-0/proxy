from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
import shutil
from config import TEMP_DIR

from services.parser_service import LogParser
from services.collector_service import LogCollector
from services.storage_service import StorageService

router = APIRouter()
TEMP_DIR = TEMP_DIR
os.makedirs(TEMP_DIR, exist_ok=True)


@router.post("/upload")
async def upload_logs(file: UploadFile = File(...)):
    """Endpoint to upload a log file(offline).
    Later: process the uploaded log file using parse_service and store it in duckdb.
    """ 
    try:
        temp_path = os.path.join(TEMP_DIR, file.filename)
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return {"status": "File uploaded successfully", "message": f"{file.filename} uploaded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post("/collect")
async def collect_logs():
    """Endpoint to collect logs from the local system(offline).
    Later: collect logs using collect_service, process them and store in duckdb.
    """
    try:
        collector = LogCollector()
        collected_files = collector.collect_local()
        return {"status": "Logs collected successfully", "collected_files": [str(f) for f in collected_files]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to collect logs: {str(e)}")

@router.post("/parse")
def parse_uploaded_log():
    """Endpoint to parse an uploaded log file(offline).
    Later: parse the uploaded log file using parse_service and return parsed data.
    """
    try:
        structured_data = {}
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isdir(file_path):
                continue  # Skip directories
            with open(file_path, 'r', errors="ignore") as f:
                content = f.read()

            lines = content.splitlines()
            try:
                df = LogParser.parse_syslog_lines(lines)
            except Exception:
                df = LogParser.parse_generic_text(lines)
            structured_data[filename] = df.shape[0]  # number of rows
        return {"status": "Logs parsed successfully", "parsed_files": structured_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse logs: {str(e)}")

@router.post("/store")
def store_parsed_logs():
    try:
        stored_tables = []
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isdir(file_path):
                continue  # Skip directories
            with open(file_path, "r", errors="ignore") as f:
                content = f.read()
            # Parse first
            lines = content.splitlines()
            try:
                df = LogParser.parse_syslog_lines(lines)
            except:
                df = LogParser.parse_generic_text(lines)
            table_name = filename.replace(".", "_")
            StorageService.insert_polars_df(df)
            stored_tables.append(table_name)
        return {"status": "success", "stored_tables": stored_tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query")
def query_logs(query: str):
    try:
        result = StorageService.query_logs(query)
        return {"status": "success", "result": result.to_dicts() if hasattr(result, 'to_dicts') else result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
