from fastapi import APIRouter
from core.database import get_db_collection
from services.ai_engine import AIEngine
from core.isolation_validator import IsolationValidator
from config import DEPLOYMENT_MODE

router = APIRouter()

@router.get("/")
def health_check():
    """Comprehensive health check"""
    status = {
        "status": "ok",
        "message": "System is Running"
    }

    return status

@router.get("/isolation")
def check_isolation():
    """
    Validate system isolation status
    
    Checks:
    - Internet connectivity
    - Network interfaces
    - External API accessibility
    
    For true air-gap deployment, should return:
    - isolation_level: "fully_isolated"
    - compliant: true
    - warnings: []
    """
    validator = IsolationValidator()
    report = validator.validate_isolation()
    
    return {
        "status": "ok" if report["compliant"] else "warning",
        "report": report,
        "recommendation": (
            "System is properly isolated" if report["compliant"]
            else "System is not fully isolated - review warnings"
        )
    }

@router.get("/config")
def get_frontend_config():
    """Frontend configuration endpoint"""
    return {
        "api_version": "1.0.0",
        "deployment_mode": DEPLOYMENT_MODE,
        "features": {
            "ssh_collection": True,
            "usb_collection": True,
            "soup_updates": True,
            "ai_analysis": True
        }
    }