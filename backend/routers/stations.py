from fastapi import APIRouter, HTTPException
from backend.services.orbits import get_satellite_coords, get_trajectory
from backend.services.soniks_api import fetch, fetch_all_paginated
from backend.services.calculate_satellite_coverage import calculate_satellite_coverage 

router = APIRouter()

@router.get("/stations")
async def stations_list():
    """Get the current position of a satellite by its NORAD catalog ID.

    Args:
        norad_id: The NORAD catalog ID of the satellite.

    Returns:
        A dictionary with satellite name, latitude, longitude, and elevation in km.

    Raises:
        HTTPException: If the TLE data for the given NORAD ID is not found.
    """
    
    data = await fetch_all_paginated("stations/")
    
    print(data)
    request = []
    for station in data: 
        req = {}
        req["id"] = station["id"]
        req["name"] = station["name"]
        req["lat"] = station["lat"]
        req["lng"] = station["lng"]
        req["status"] = station["status"]
       # req["coverage_radius"] = calculate_satellite_coverage()
        request.append(req)

    return request

@router.get("/station/{id}&{altitude}")
async def station_info(id: int, altitude: int):
    """Get the current position of a satellite by its NORAD catalog ID.

    Args:
        norad_id: The NORAD catalog ID of the satellite.

    Returns:
        A dictionary with satellite name, latitude, longitude, and elevation in km.

    Raises:
        HTTPException: If the TLE data for the given NORAD ID is not found.
    """
    
    station = await fetch(f"stations/?id={id}")
    station = station[0]
    reqest = {}
    reqest["id"] = station["id"]
    reqest["name"] = station["name"]
    reqest["lat"] = station["lat"]
    reqest["lng"] = station["lng"]
    reqest["status"] = station["status"]
    reqest["coverage_radius"] = calculate_satellite_coverage(station["altitude"],station["min_horizon"],altitude)


    return reqest
