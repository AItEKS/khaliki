from fastapi import APIRouter, HTTPException
from backend.services.orbits import get_satellite_coords, get_trajectory
from backend.services.soniks_api import fetch


router = APIRouter()

@router.get("/position/{norad_id}")
async def satellite_position(norad_id: int):
    """Get the current position of a satellite by its NORAD catalog ID.

    Args:
        norad_id: The NORAD catalog ID of the satellite.

    Returns:
        A dictionary with satellite name, latitude, longitude, and elevation in km.

    Raises:
        HTTPException: If the TLE data for the given NORAD ID is not found.
    """
    tles = await fetch("latesttles/")
    tle_entry = next((t for t in tles if t["satellite"]["norad_cat_id"] == norad_id), None)

    if not tle_entry:
        raise HTTPException(status_code=404, detail="TLE not found")

    tle1 = tle_entry["latest"]["tle1"]
    tle2 = tle_entry["latest"]["tle2"]
    tle0 = tle_entry["latest"]["tle0"]

    return get_satellite_coords(tle1, tle2, tle0)


@router.get("/trajectory/{norad_id}")
async def satellite_trajectory(norad_id: int, minutes: int = 15, step: int = 30):
    """Get the satellite trajectory for a given NORAD ID over a time interval.

    Args:
        norad_id: The NORAD catalog ID of the satellite.
        minutes: Duration in minutes for the trajectory calculation. Defaults to 15.
        step: Time step in seconds between trajectory points. Defaults to 30.

    Returns:
        A list of dictionaries with latitude, longitude, elevation, and timestamp.

    Raises:
        HTTPException: If the TLE data for the given NORAD ID is not found.
    """
    tles = await fetch("latesttles/")
    tle_entry = next((t for t in tles if t["satellite"]["norad_cat_id"] == norad_id), None)

    if not tle_entry:
        raise HTTPException(status_code=404, detail="TLE not found")

    tle1 = tle_entry["latest"]["tle1"]
    tle2 = tle_entry["latest"]["tle2"]
    tle0 = tle_entry["latest"]["tle0"]

    return get_trajectory(tle1, tle2, tle0, minutes, step)


@router.get("/next_passes")
async def next_passes(limit: int = 10):
    """
    Get the list of upcoming satellite passes.

    Args:
        limit: Maximum number of future passes to return. Defaults to 10.

    Returns:
        A list of dictionaries, each containing:
            - satellite_name: Name of the satellite.
            - norad_id: NORAD catalog ID of the satellite.
            - tle: Dictionary with TLE lines (tle0, tle1, tle2).
            - start: Start time of the pass.
            - end: End time of the pass.

    Raises:
        HTTPException: If the observations data cannot be fetched or is empty.
    """
    observation = await fetch("observations/")

    future_passes = [obs for obs in observation if obs["status"] == "future" and obs.get("tle") is not None]
    future_passes.sort(key=lambda x: x["start"])
    future_passes = future_passes[:limit]

    result = []
    for obs in future_passes:
        tle = obs.get("tle", {})
        result.append({
            "satellite_name": tle.get("tle0", "Unknown"),
            "norad_id": obs.get("norad_cat_id"),
                        "tle": {
                "tle0": tle.get("tle0"),
                "tle1": tle.get("tle1"),
                "tle2": tle.get("tle2")
            },
            "start": obs.get("start"),
            "end": obs.get("end")
        })

    return result