from fastapi import APIRouter, HTTPException
from backend.services.soniks_api import fetch, fetch_all_paginated
from backend.services.calculate_satellite_coverage import calculate_satellite_coverage
from typing import List, Dict, Any

router = APIRouter()


@router.get("/stations", response_model=List[Dict[str, Any]], summary="Get list of ground stations")
async def stations_list() -> List[Dict[str, Any]]:
    """Retrieve a list of current ground stations.

    This endpoint fetches a paginated list of ground stations and returns
    their details including ID, name, latitude, longitude, and status.

    Returns:
        List of dictionaries with station details:
            - id: Station ID.
            - name: Station name.
            - lat: Latitude.
            - lng: Longitude.
            - status: Current status.
    """
    stations = await fetch_all_paginated("stations/")
    response = []

    for station in stations:
        response.append({
            "id": station["id"],
            "name": station["name"],
            "lat": station["lat"],
            "lng": station["lng"],
            "status": station["status"],
        })

    return response


@router.get("/station/{station_id}/{altitude}", response_model=Dict[str, Any], summary="Get detailed info about a ground station")
async def station_info(station_id: int, altitude: int) -> Dict[str, Any]:
    """Retrieve detailed information about a specific ground station.

    Args:
        station_id (int): The ID of the ground station.
        altitude (int): Altitude at which to calculate coverage radius.

    Returns:
        Dictionary with station details and coverage radius.

    Raises:
        HTTPException: If the station is not found.
    """
    stations = await fetch(f"stations/?id={station_id}")
    if not stations:
        raise HTTPException(status_code=404, detail=f"Station with id {station_id} not found")

    station = stations[0]

    coverage_radius = calculate_satellite_coverage(
        station.get("altitude", 0),
        station.get("min_horizon", 0),
        altitude
    )

    return {
        "id": station["id"],
        "name": station["name"],
        "lat": station["lat"],
        "lng": station["lng"],
        "status": station["status"],
        "coverage_radius": coverage_radius,
    }

@router.get("/station/history/{station_id}", response_model=List[Dict[str, Any]], summary="Get observation history for a ground station")
async def station_history(station_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve historical observation data for a specific ground station.

    Args:
        station_id (int): The ID of the ground station.
        limit (int, optional): Max number of observations to return. Defaults to 20.

    Returns:
        List of dictionaries containing historical observations:
            - id: Observation ID.
            - status: Observation status.
            - norad_cat_id: NORAD catalog ID of satellite.
            - satellite_name: Name of the satellite.
            - station_name: Name of the ground station.
            - start: Observation start time (ISO format without trailing 'Z').
            - end: Observation end time (ISO format without trailing 'Z').
            - observation_frequency: Frequency of observation.

    Raises:
        HTTPException: If no observations are found.
    """
    observations = await fetch(f"observations/?ground_station={station_id}")

    if not observations:
        return []

    filtered_obs = [obs for obs in observations if obs.get("status") != "future"]
    sorted_obs = sorted(filtered_obs, key=lambda x: x.get("start", ""), reverse=True)[:limit]

    result = []
    for obs in sorted_obs:
        satellite_name = obs.get("tle", {}).get("tle0", "Unknown")
        start_time = obs.get("start", "").rstrip("Z")
        end_time = obs.get("end", "").rstrip("Z")

        result.append({
            "id": obs.get("id"),
            "status": obs.get("status"),
            "norad_cat_id": obs.get("norad_cat_id"),
            "satellite_name": satellite_name,
            "station_name": obs.get("station_name"),
            "start": start_time,
            "end": end_time,
            "observation_frequency": obs.get("observation_frequency"),
        })

    return result