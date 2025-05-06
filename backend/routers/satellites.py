from fastapi import APIRouter, HTTPException
from backend.services.soniks_api import fetch

router = APIRouter(
    prefix="/satellites",  
    tags=["Satellites"],
    responses={500: {"description": "Internal Server Error"}},
)

@router.get("/", summary="Get all satellites", response_description="List of satellites")
async def get_satellites():
    """Fetch the list of satellites from the backend service.

    Returns:
        List[dict]: A list of satellite data.

    Raises:
        HTTPException: If fetching data fails, returns HTTP 500.
    """
    try:
        data = await fetch("satellites/")
        return data
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch satellites: {str(exc)}"
        )