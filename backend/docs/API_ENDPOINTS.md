# API Endpoints Documentation

## Overview
This document describes all available API endpoints for the Log Analysis System.

## Base URL
All endpoints are prefixed with `/api/v1`

## Authentication
Currently, no authentication is implemented. All endpoints are publicly accessible.

## Rate Limiting
No rate limiting is currently implemented.

## Error Response Format
All endpoints return standardized error responses:
```json
{
  "detail": "Error message description"
}
```

## Endpoints

### Health Check
- **GET** `/health/`
- **Status**: ✅ Fully Implemented
- **Description**: Comprehensive health check for API, database, and AI models
- **Parameters**: None
- **Request Example**:
  ```bash
  GET /api/v1/health/
  ```
- **Success Response** (200):
  ```json
  {
    "status": "ok",
    "message": "System is Running"
  }
  ```
- **Error Response** (500):
  ```json
  {
    "detail": "Health check failed: Database connection error"
  }
  ```

### Log Management

#### Upload Logs
- **POST** `/logs/upload`
- **Status**: ✅ Fully Implemented
- **Description**: Upload a log file for offline analysis
- **Supported Formats**: .log, .txt, .evtx, .json, .csv, .evt, .gz
- **Parameters**:
  - `file` (file): Log file to upload (multipart/form-data)
- **Validation**:
  - File size limit: Not specified
  - File type validation: Based on extension
- **Request Example**:
  ```bash
  POST /api/v1/logs/upload
  Content-Type: multipart/form-data

  file: example.log
  ```
- **Success Response** (200):
  ```json
  {
    "status": "success",
    "message": "File uploaded successfully",
    "filename": "example.log"
  }
  ```
- **Error Responses**:
  - 400: Invalid file format
    ```json
    {
      "detail": "Unsupported file format. Supported: .log, .txt, .evtx, .json, .csv, .evt, .gz"
    }
    ```
  - 500: Upload failed
    ```json
    {
      "detail": "Upload failed: Disk full"
    }
    ```

#### Collect Local Logs
- **POST** `/logs/collect/local`
- **Description**: Collect logs from the local system (cross-platform)
- **Supported OS**: Windows, Linux, macOS
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Collected logs from Windows",
    "system": "Windows",
    "files_collected": 5,
    "files": ["path/to/log1.log", "path/to/log2.log"]
  }
  ```

#### Collect from Directory
- **POST** `/logs/collect/directory`
- **Description**: Collect logs from a specific directory
- **Parameters**:
  - `directory_path` (string): Path to the directory
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Collected logs from /path/to/logs",
    "files_collected": 10,
    "files": ["file1.log", "file2.log"]
  }
  ```

#### Parse Uploaded Logs
- **POST** `/logs/parse`
- **Description**: Parse all uploaded/collected logs in TEMP_DIR
- **Response**:
  ```json
  {
    "status": "success",
    "files_parsed": 3,
    "details": {
      "file1.log": {
        "rows": 100,
        "parser": "syslog",
        "columns": ["timestamp", "host", "message"]
      }
    }
  }
  ```

#### Store Parsed Logs
- **POST** `/logs/store`
- **Description**: Store parsed logs into DuckDB
- **Response**:
  ```json
  {
    "status": "success",
    "files_stored": 3,
    "total_rows": 500,
    "files": ["file1.log", "file2.log", "file3.log"]
  }
  ```

#### Query Logs
- **GET** `/logs/query`
- **Description**: Execute SQL query on stored logs
- **Parameters**:
  - `query` (string): SQL query string
- **Security**: Basic SQL injection prevention (blocks DROP, DELETE, etc.)
- **Example**: `SELECT * FROM logs WHERE is_anomaly = TRUE LIMIT 10`
- **Response**:
  ```json
  {
    "status": "success",
    "rows": 5,
    "data": [["2023-01-01", "host1", "message1"], ...]
  }
  ```

#### Clear Temp Logs
- **DELETE** `/logs/clear`
- **Description**: Clear all temporary log files
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Cleared 5 temporary files"
  }
  ```

#### Get Collection Status
- **GET** `/logs/status`
- **Description**: Get current status of log collection and storage
- **Response**:
  ```json
  {
    "status": "operational",
    "system": "Windows",
    "temp_storage": {
      "files": 3,
      "size_mb": 15.5
    },
    "database": {
      "total_logs": 1000,
      "unique_hosts": 5,
      "anomalies": 25
    }
  }
  ```

### Analysis

#### Run Analysis
- **POST** `/analysis/run`
- **Description**: Run AI anomaly detection on all stored logs
- **Response**:
  ```json
  {
    "status": "success",
    "analyzed": 100,
    "anomalies_found": 5,
    "results": ["anomaly1", "anomaly2"]
  }
  ```

#### Get Analysis Results
- **GET** `/analysis/results`
- **Description**: Retrieve detected anomalies
- **Response**:
  ```json
  {
    "status": "success",
    "anomalies": [
      {
        "timestamp": "2023-01-01T10:00:00",
        "host": "server1",
        "message": "Error message",
        "score": 0.85
      }
    ],
    "count": 10
  }
  ```

### SOUP (Secure Offline Update Protocol)

#### Apply SOUP Update
- **POST** `/soup/update`
- **Description**: Apply SOUP updates using an uploaded file
- **Request**: Multipart form data with file
- **Status**: Not fully implemented
- **Response**:
  ```json
  {
    "filename": "update.soup",
    "content_type": "application/octet-stream",
    "status": "SOUP file received successfully"
  }
  ```

#### Get SOUP Status
- **GET** `/soup/status`
- **Description**: Get the current status of SOUP updates
- **Status**: Not implemented
- **Response**:
  ```json
  {
    "status": "SOUP status functionality not implemented yet"
  }
  ```

## Error Responses
All endpoints return standardized error responses:
```json
{
  "detail": "Error message"
}
```

## Authentication
Currently, no authentication is implemented.

## Rate Limiting
No rate limiting is currently implemented.

## Data Models

### UploadResponse
```python
class UploadResponse(BaseModel):
    status: str
    message: str
    filename: str
