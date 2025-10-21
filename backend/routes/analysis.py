from fastapi import APIRouter, HTTPException
from services.ai_engine import AIEngine
from services.storage_service import StorageService
from config import MODELS_DIR

router = APIRouter()
ai_engine = AIEngine()

@router.post("/run")
async def run_analysis():
    """Run AI anomaly detection on all stored logs"""
    try:
        # Fetch all logs from DuckDB
        result = StorageService.query_logs("SELECT message, id FROM logs WHERE anomaly_score = 0")

        if not result:
            return {"status": "no_data", "message": "No logs to analyze"}

        messages = [row[0] for row in result]
        ids = [row[1] for row in result]

        # Run AI analysis
        analysis_results = ai_engine.analyze(messages)

        # Update database with scores
        conn = StorageService.get_connection()
        for idx, score in enumerate(analysis_results['scores']):
            conn.execute(
                "UPDATE logs SET anomaly_score = ?, is_anomaly = ? WHERE id = ?",
                (score, score > 0.5, ids[idx])
            )

        return {
            "status": "success",
            "analyzed": analysis_results['total_analyzed'],
            "anomalies_found": analysis_results['anomaly_count'],
            "results": analysis_results['anomalies']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_analysis_results():
    """Retrieve detected anomalies"""
    try:
        result = StorageService.query_logs(
            "SELECT timestamp, host, message, anomaly_score FROM logs WHERE is_anomaly = TRUE ORDER BY anomaly_score DESC LIMIT 100"
        )

        anomalies = [
            {
                "timestamp": row[0],
                "host": row[1],
                "message": row[2],
                "score": row[3]
            }
            for row in result
        ]

        return {"status": "success", "anomalies": anomalies, "count": len(anomalies)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
