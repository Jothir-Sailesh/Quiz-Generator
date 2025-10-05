from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def analytics_status():
    return {"analytics": "active"}

