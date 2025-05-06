from fastapi import APIRouter, HTTPException
from backend.services.orbits import get_satellite_coords, get_trajectory
from backend.services.soniks_api import fetch
from typing import List, Dict, Any, Optional

router = APIRouter()


@router.get("/position/{norad_id}", response_model=Dict[str, Any], summary="Get current satellite position")
async def satellite_position(norad_id: int) -> Dict[str, Any]:
    """Get the current position of a satellite by its NORAD catalog ID.

    Args:
        norad_id (int): The NORAD catalog ID of the satellite.

    Returns:
        dict: Satellite position data including name, latitude, longitude, and elevation in km.

    Raises:
        HTTPException: If the TLE data for the given NORAD ID is not found.
    """
    tles = await fetch("latesttles/", params={"norad_cat_id": norad_id})

    if not tles:
        raise HTTPException(status_code=404, detail=f"TLE not found for NORAD ID {norad_id}")

    tle_entry = tles[0]
    latest = tle_entry.get("latest", {})

    tle1 = latest.get("tle1")
    tle2 = latest.get("tle2")
    tle0 = latest.get("tle0")

    if not all([tle1, tle2, tle0]):
        raise HTTPException(status_code=500, detail="Incomplete TLE data")

    return get_satellite_coords(tle1, tle2, tle0)

@router.get("/trajectory/{norad_id}", response_model=List[Dict[str, Any]], summary="Get satellite trajectory")
async def satellite_trajectory(
    norad_id: int,
    minutes: int = 15,
    step: int = 30
) -> List[Dict[str, Any]]:
    """Get the satellite trajectory for a given NORAD ID over a time interval.

    Args:
        norad_id (int): The NORAD catalog ID of the satellite.
        minutes (int, optional): Duration in minutes for the trajectory calculation. Defaults to 15.
        step (int, optional): Time step in seconds between trajectory points. Defaults to 30.

    Returns:
        List[dict]: Trajectory points with latitude, longitude, elevation, and timestamp.

    Raises:
        HTTPException: If the TLE data for the given NORAD ID is not found.
    """
    tles = await fetch("latesttles/", params={"norad_cat_id": norad_id})

    if not tles:
        raise HTTPException(status_code=404, detail=f"TLE not found for NORAD ID {norad_id}")

    tle_entry = tles[0]
    latest = tle_entry.get("latest", {})

    tle1 = latest.get("tle1")
    tle2 = latest.get("tle2")
    tle0 = latest.get("tle0")

    if not all([tle1, tle2, tle0]):
        raise HTTPException(status_code=500, detail="Incomplete TLE data")

    return get_trajectory(tle1, tle2, tle0, minutes, step)


@router.get("/station/next_passes/{station_id}", response_model=List[Dict[str, Any]], summary="Get upcoming satellite passes for a ground station")
async def next_passes(station_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get the upcoming satellite passes for a given ground station.

    Args:
        station_id (int): The ID of the ground station.
        limit (int, optional): Maximum number of future passes to return. Defaults to 10.

    Returns:
        List[dict]: Each dict contains satellite_name, norad_id, TLE lines, start and end times.

    Raises:
        HTTPException: If no future passes with TLE data are found for the station.
    """
    observations = await fetch("observations/")

    future_passes = [
        obs for obs in observations
        if obs.get("ground_station") == station_id
        and obs.get("status") == "future"
        and obs.get("tle") is not None
    ]

    if not future_passes:
        return []

    future_passes.sort(key=lambda obs: obs.get("start", ""))

    limited_passes = future_passes[:limit]

    result = []
    for obs in limited_passes:
        tle = obs.get("tle", {})
        result.append({
            "satellite_name": tle.get("tle0", "Unknown"),
            "norad_id": obs.get("norad_cat_id"),
            "tle": {
                "tle0": tle.get("tle0"),
                "tle1": tle.get("tle1"),
                "tle2": tle.get("tle2"),
            },
            "start": obs.get("start"),
            "end": obs.get("end"),
        })

    return result