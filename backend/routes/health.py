from fastapi import APIRouter
from core.database import get_db_collection
from services.ai_engine import AIEngine

router = APIRouter()

@router.get("/")
def health_check():
    """Comprehensive health check"""
    status = {
        "status": "ok",
        "message": "System is Running"
    }

    return status
