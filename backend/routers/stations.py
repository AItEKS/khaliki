from fastapi import APIRouter, HTTPException
from backend.services.orbits import get_satellite_coords, get_trajectory
from backend.services.soniks_api import fetch, fetch_all_paginated
from backend.services.calculate_satellite_coverage import calculate_satellite_coverage 

router = APIRouter()

@router.get("/stations")
async def stations_list():
    """Retrieve a list of current ground stations.

    This endpoint fetches a paginated list of ground stations and returns
    their details including ID, name, latitude, longitude, and status.

    Returns:
        A list of dictionaries with each dictionary containing:
            - id: The ID of the station.
            - name: The name of the station.
            - lat: The latitude of the station.
            - lng: The longitude of the station.
            - status: The current status of the station.
    """
    data = await fetch_all_paginated("stations/")
    
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
    """Retrieve detailed information about a specific ground station.

    Args:
        id: The ID of the ground station.
        altitude: The altitude at which to calculate the coverage radius.

    Returns:
        A dictionary with details about the station including:
            - id: The ID of the station.
            - name: The name of the station.
            - lat: The latitude of the station.
            - lng: The longitude of the station.
            - status: The current status of the station.
            - coverage_radius: The calculated coverage radius based on altitude.
    
    Raises:
        HTTPException: If the station data is not found.
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

@router.get("/station/history/{id}")
async def station_hist(id: int, limit: int = 20):
    """Retrieve historical observation data for a specific ground station.

    Args:
        id: The ID of the ground station.
        limit: The maximum number of observations to return. Default is 20.

    Returns:
        A list of dictionaries containing historical observations with keys:
            - id: The observation ID.
            - status: The status of the observation.
            - norad_cat_id: The NORAD catalog ID of the observed satellite.
            - satellite_name: The name of the observed satellite.
            - station_name: The name of the ground station.
            - start: The start time of the observation.
            - end: The end time of the observation.
            - observation_frequency: The frequency of the observation.

    Raises:
        HTTPException: If no observations are found for the given station ID.
    """
    observations = await fetch(f"observations/?ground_station={id}")

    if not observations:
        return []
    
    filtered_obs = [obs for obs in observations if obs.get("status") != "future"]
    sorted_obs = sorted(filtered_obs, key=lambda x: x["start"], reverse=True)[:limit]

    result = []
    for obs in sorted_obs:
        result.append({
            "id": obs.get("id"),
            "status": obs.get("status"),
            "norad_cat_id": obs.get("norad_cat_id"),
            "satellite_name": obs.get("tle", {}).get("tle0", "Unknown"),
            "station_name": obs.get("station_name"),
            "start": obs.get("start"),
            "end": obs.get("end"),
            "observation_frequency": obs.get("observation_frequency")
        })

    return result