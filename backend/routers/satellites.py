from fastapi import APIRouter, Query, HTTPException
from backend.services.soniks_api import fetch

router = APIRouter()


@router.get("/")
async def get_satellites():
    try:
        data = await fetch("satellites/")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении спутников: {str(e)}")

    return data