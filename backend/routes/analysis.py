from fastapi import APIRouter, HTTPException
from services.storage_service import StorageService
from core.detection_engine import DetectionEngine
import json

router = APIRouter()
detection_engine = DetectionEngine()

@router.post("/analyze/comprehensive")
async def comprehensive_analysis():
    """
    Run comprehensive analysis using:
    - AI anomaly detection
    - Rule-based detection
    - Threat intelligence matching
    - TTP detection
    """
    try:
        # Fetch unanalyzed logs
        logs = StorageService.query_logs(
            "SELECT id, timestamp, host, process, message FROM logs WHERE detections IS NULL LIMIT 5000"
        )
        
        if not logs:
            return {"status": "no_data", "message": "No new logs to analyze"}
        
        log_entries = [{'id': log[0], 'timestamp': log[1], 'host': log[2], 'process': log[3], 'message': log[4]} for log in logs]
        
        results = detection_engine.batch_analyze(log_entries)
        
        threats_found = 0
        with StorageService.get_connection() as conn:
            for result in results:
                log_id = result['log_entry']['id']
                if result['is_threat']:
                    threats_found += 1
                    severity = result['severity']
                    score = result['detections'][0]['score'] if result['detections'] else 0.0
                    detections_json = json.dumps(result['detections'])
                    
                    conn.execute("UPDATE logs SET is_anomaly = TRUE, anomaly_score = ?, severity = ?, detections = ? WHERE id = ?", (score, severity, detections_json, log_id))
                else:
                    conn.execute("UPDATE logs SET detections = '[]' WHERE id = ?", (log_id,))

        threats = [r for r in results if r['is_threat']]
        
        return {
            "status": "success",
            "analyzed": len(results),
            "threats_found": threats_found,
            "severity_breakdown": {
                "critical": len([t for t in threats if t['severity'] == 'critical']),
                "high": len([t for t in threats if t['severity'] == 'high']),
                "medium": len([t for t in threats if t['severity'] == 'medium']),
            },
            "top_threats": threats[:20]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))