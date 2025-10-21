from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health_check():
    """
    Check helath of endpoints & app
    """
    return {"status" : "ok", "message" : "System is Running"}