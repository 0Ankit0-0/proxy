# API Endpoints Documentation

## Overview
This document describes all available API endpoints for the Project Quorum Log Analysis System.

## Base URL
The backend runs on `http://localhost:8000` by default. All endpoints are relative to this base URL.

## Authentication
Currently, no authentication is implemented. All endpoints are publicly accessible.

## Error Response Format
All endpoints return standardized error responses:
```json
{
  "detail": "Error message description"
}
```

## Endpoints

### Health Check (`/health`)

- **GET** `/health/`
- **Status**: ✅ Fully Implemented
- **Description**: Comprehensive health check for API, database, and AI models.
- **Success Response** (200):
  ```json
  {
    "status": "ok",
    "message": "System is Running"
  }
  ```

- **GET** `/health/isolation`
- **Status**: ✅ Fully Implemented
- **Description**: Validates the isolation status of the system.
- **Success Response** (200):
  ```json
  {
    "isolation_level": "fully_isolated",
    "compliant": true,
    "warnings": []
  }
  ```

### Log Management (`/logs`)

#### Upload Logs
- **POST** `/logs/upload`
- **Status**: ✅ Fully Implemented
- **Description**: Upload a log file for offline analysis.
- **Request Body**: `multipart/form-data` with a `file` field.
- **Success Response** (200):
  ```json
  {
    "status": "success",
    "message": "File uploaded successfully",
    "filename": "example.log"
  }
  ```

#### Collect Logs from Directory
- **POST** `/logs/collect/directory`
- **Status**: ✅ Fully Implemented
- **Description**: Collect logs from a specific directory on the server.
- **Request Body**:
    ```json
    {
        "directory_path": "/path/to/logs"
    }
    ```
- **Success Response** (200):
  ```json
  {
    "status": "success",
    "message": "Collected logs from /path/to/logs",
    "files_collected": 1,
    "files": ["example.log"]
  }
  ```

#### Parse and Store Logs
- **POST** `/logs/store`
- **Status**: ✅ Fully Implemented
- **Description**: Parses all log files from the temporary directory and stores them in the database. This endpoint now handles deduplication.
- **Success Response** (200):
  ```json
  {
    "status": "success",
    "files_processed": 1,
    "total_rows_stored": 100,
    "files": ["example.log"]
  }
  ```

#### Query Logs
- **GET** `/logs/query/{query_name}`
- **Status**: ✅ Fully Implemented
- **Description**: Execute a pre-defined, safe query on the stored logs.
- **Path Parameters**:
  - `query_name` (string): The name of the query to execute. Allowed values: `get_anomalies`, `get_recent`, `count_by_host`.
- **Query Parameters**:
  - `limit` (int, optional): The maximum number of rows to return. Defaults to 100.
- **Example**: `GET /logs/query/get_anomalies?limit=10`
- **Success Response** (200):
  ```json
  {
    "status": "success",
    "rows": 5,
    "data": [
        // ... array of results
    ]
  }
  ```

### Analysis (`/analysis`)

#### Comprehensive Analysis
- **POST** `/analysis/comprehensive`
- **Status**: ✅ Fully Implemented
- **Description**: Runs the full multi-layered detection engine on all unanalyzed logs. This includes anomaly, TTP, IoC, and rule-based detection. The results are stored in the database.
- **Success Response** (200):
  ```json
  {
    "status": "success",
    "analyzed": 5000,
    "threats_found": 47,
    "severity_breakdown": {
      "critical": 3,
      "high": 12,
      "medium": 25,
      "low": 7
    },
    "top_threats": [
      {
        "log_entry": {
          "message": "mimikatz.exe executed: sekurlsa::logonpasswords"
        },
        "is_threat": true,
        "severity": "critical",
        "detections": [
          {
            "type": "ttp",
            "name": "OS Credential Dumping",
            "score": 1.0,
            "details": {
              "ttp_id": "T1003",
              "tactic": "Credential Access"
            }
          },
          {
            "type": "rule",
            "name": "Mimikatz Credential Dumping",
            "score": 1.0
          },
          {
            "type": "ioc",
            "name": "Malicious Process Detected",
            "indicator": "mimikatz.exe"
          }
        ]
      }
    ]
  }
  ```

### SOUP (Secure Offline Update Protocol) (`/soup`)

#### Apply SOUP Update
- **POST** `/soup/update`
- **Status**: ✅ Fully Implemented
- **Description**: Apply a SOUP update package. The endpoint handles extraction, verification (checksums and digital signature), and atomic application of updates. Includes audit logging.
- **Request Body**: `multipart/form-data` with a `file` field containing the `.soup` package.
- **Success Response** (200):
  ```json
  {
    "status": "success",
    "message": "SOUP update applied successfully",
    "version": "2.1.0",
    "applied_updates": {
        "models": ["iforest_model_v2.pkl"],
        "rules": [],
        "threat_intel": []
    },
    "timestamp": "2025-10-24T12:00:00Z"
  }
  ```

#### Get SOUP Status
- **GET** `/soup/status`
- **Status**: ✅ Fully Implemented
- **Description**: Get the current status of SOUP updates and history.
- **Success Response** (200):
  ```json
  {
    "status": "operational",
    "current_models": ["iforest_model.pkl"],
    "last_update": { ... },
    "update_count": 1,
    "recent_updates": [ ... ]
  }
  ```