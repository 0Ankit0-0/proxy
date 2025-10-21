from fastapi import APIRouter
from core.database import get_db_collection
from services.ai_engine import AIEngine

router = APIRouter()

@router.get("/")
def health_check():
    """Comprehensive health check"""
    status = {
        "api": "ok",
        "database": "checking",
        "ai_models": "checking"
    }

    # Check database
    try:
        conn = get_db_collection()
        conn.execute("SELECT 1")
        status["database"] = "ok"
    except Exception as e:
        status["database"] = f"error: {str(e)}"

    # Check AI models
    try:
        ai = AIEngine()
        status["ai_models"] = "ok"
    except Exception as e:
        status["ai_models"] = f"error: {str(e)}"

    return status
