from fastapi import APIRouter, HTTPException
from festival_service import get_all_festivals, get_festival_by_id

router = APIRouter(prefix="/festivals", tags=["festivals"])

@router.get("/")
def read_festivals():
    return get_all_festivals()

@router.get("/{festival_id}")
def read_festival(festival_id: int):
    festival = get_festival_by_id(festival_id)
    if not festival:
        raise HTTPException(status_code=404, detail="Festival not found")
    return festival