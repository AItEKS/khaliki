from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.orbits import get_satellite_coords
from backend.services.soniks_api import fetch
import asyncio


router = APIRouter()

@router.websocket("/ws/position/{norad_id}")
async def websocket_position(websocket: WebSocket, norad_id: int):
    await websocket.accept()

    try:
        tles = await fetch("latesttles/")
        tle_entry = next((t for t in tles if t["satellite"]["norad_cat_id"] == norad_id), None)

        if not tle_entry:
            await websocket.send_json({"error": "TLE not found"})
            await websocket.close()
            return

        tle1 = tle_entry["latest"]["tle1"]
        tle2 = tle_entry["latest"]["tle2"]
        tle0 = tle_entry["latest"]["tle0"]

        while True:
            position = get_satellite_coords(tle1, tle2, tle0)
            await websocket.send_json(position)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print(f"Websocket {norad_id} disconnected")