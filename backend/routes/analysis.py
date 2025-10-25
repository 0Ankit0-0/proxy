from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.storage_service import StorageService
from core.detection_engine import DetectionEngine
import json
import asyncio
import os

router = APIRouter()
detection_engine = DetectionEngine()

# File path for progress tracking
PROGRESS_FILE = "data/analysis_progress.json"

@router.post("/analyze/comprehensive")
async def comprehensive_analysis(background_tasks: BackgroundTasks):
    """
    Run comprehensive analysis in the background with progress tracking.
    Returns immediately, while analysis runs asynchronously.
    """
    background_tasks.add_task(run_analysis_task)
    
    return {
        "status": "started",
        "message": "Comprehensive analysis started in background.",
        "check_progress_at": "/analysis/progress"
    }


@router.get("/analysis/progress")
async def get_analysis_progress():
    """Fetch current analysis progress."""
    if not os.path.exists(PROGRESS_FILE):
        return {"status": "idle", "progress": 0, "message": "No analysis running."}
    
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)


async def run_analysis_task():
    """Performs the full comprehensive analysis asynchronously and updates progress."""
    try:
        # Initialize progress
        save_progress(0, "Fetching logs from database...")

        logs = StorageService.query_logs(
            "SELECT id, timestamp, host, process, message FROM logs WHERE detections IS NULL LIMIT 5000"
        )

        if not logs:
            save_progress(100, "No new logs to analyze.")
            return

        log_entries = [
            {'id': log[0], 'timestamp': log[1], 'host': log[2], 'process': log[3], 'message': log[4]}
            for log in logs
        ]

        total = len(log_entries)
        analyzed = 0
        threats_found = 0

        save_progress(5, f"Analyzing {total} logs...")

        results = detection_engine.batch_analyze(log_entries)

        with StorageService.get_connection() as conn:
            for result in results:
                analyzed += 1
                log_id = result['log_entry']['id']

                if result['is_threat']:
                    threats_found += 1
                    severity = result['severity']
                    score = result['detections'][0]['score'] if result['detections'] else 0.0
                    detections_json = json.dumps(result['detections'])
                    conn.execute(
                        "UPDATE logs SET is_anomaly = TRUE, anomaly_score = ?, severity = ?, detections = ? WHERE id = ?",
                        (score, severity, detections_json, log_id)
                    )
                else:
                    conn.execute("UPDATE logs SET detections = '[]' WHERE id = ?", (log_id,))
                
                # Update progress every 100 logs
                if analyzed % 100 == 0 or analyzed == total:
                    percent = round((analyzed / total) * 100, 2)
                    save_progress(percent, f"Analyzed {analyzed}/{total} logs...")

                # Allow other background tasks to run
                await asyncio.sleep(0.01)

        save_progress(100, f"Completed analysis. Threats found: {threats_found}")

    except Exception as e:
        save_progress(100, f"Error: {str(e)}")


def save_progress(percent: float, message: str):
    """Save current progress to a JSON file for monitoring."""
    data = {
        "status": "running" if percent < 100 else "completed",
        "progress": percent,
        "message": message
    }
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)
