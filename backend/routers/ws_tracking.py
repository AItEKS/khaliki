from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from backend.services.orbits import get_satellite_coords
from backend.services.soniks_api import fetch
import asyncio
from typing import Optional


router = APIRouter()


@router.websocket("/ws/position/{norad_id}")
async def websocket_position(websocket: WebSocket, norad_id: int):
    """WebSocket endpoint to stream satellite position updates by NORAD ID.

    Args:
        websocket (WebSocket): The WebSocket connection.
        norad_id (int): The NORAD catalog ID of the satellite.

    Sends:
        JSON: Satellite position data every 5 seconds or an error message if TLE not found.

    Handles:
        WebSocketDisconnect: Logs disconnection event.
    """
    await websocket.accept()

    try:
        tles = await fetch("latesttles/")

        tle_entry: Optional[dict] = next(
            (t for t in tles if t["satellite"]["norad_cat_id"] == norad_id), None
        )

        if not tle_entry:
            await websocket.send_json({"error": "TLE not found for NORAD ID"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        tle1 = tle_entry["latest"]["tle1"]
        tle2 = tle_entry["latest"]["tle2"]
        tle0 = tle_entry["latest"]["tle0"]

        while True:
            position = get_satellite_coords(tle1, tle2, tle0)
            await websocket.send_json(position)
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        print(f"WebSocket connection closed for NORAD ID: {norad_id}")