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