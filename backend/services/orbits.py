from skyfield.api import EarthSatellite, load, wgs84, utc
from datetime import datetime, timedelta


def get_satellite_coords(tle1: str, tle2: str, tle0: str = "SAT") -> dict:
    """Returns the current geodetic coordinates of a satellite from TLE data.
    
    Args:
        tle1: The first line of the TLE (Two-Line Element set).
        tle2: The second line of the TLE.
        tle0: The satellite name or identifier. Defaults to "SAT".
    
    Returns:
        A dictionary containing:
            name: The satellite name.
            lat: Subpoint latitude in degrees.
            lon: Subpoint longitude in degrees.
            elevation_km: Subpoint elevation in kilometers.
    """
    ts = load.timescale()
    t = ts.now()
    satellite = EarthSatellite(tle1, tle2, tle0, ts)
    geocentric = satellite.at(t)
    subpoint = geocentric.subpoint()
    
    return {
        "name": tle0,
        "lat": subpoint.latitude.degrees,
        "lon": subpoint.longitude.degrees,
        "elevation_km": subpoint.elevation.km,
    }


def get_trajectory(
    tle1: str, 
    tle2: str, 
    tle0: str = "SAT", 
    minutes: int = 15, 
    step: int = 30
) -> list[dict[str, object]]:
    """Computes the satellite trajectory over a given time interval.
    
    Args:
        tle1: The first line of the TLE (Two-Line Element set).
        tle2: The second line of the TLE.
        tle0: The satellite name or identifier. Defaults to "SAT".
        minutes: Duration in minutes for which to compute the trajectory. Defaults to 15.
        step: Time step in seconds between trajectory points. Defaults to 30.
    
    Returns:
        A list of dictionaries, each containing:
            lat: Latitude in degrees.
            lon: Longitude in degrees.
            elevation_km: Elevation in kilometers.
            timestamp: ISO 8601 UTC timestamp string.
    """
    ts = load.timescale()
    satellite = EarthSatellite(tle1, tle2, tle0, ts)
    now = datetime.utcnow().replace(tzinfo=utc)
    
    # Создаем список временных точек с заданным шагом
    times = [ts.utc(now + timedelta(seconds=i)) for i in range(0, minutes * 60, step)]
    
    positions = []
    for t in times:
        geo = satellite.at(t)
        subpoint = geo.subpoint()
        positions.append({
            "lat": subpoint.latitude.degrees,
            "lon": subpoint.longitude.degrees,
            "elevation_km": subpoint.elevation.km,
            "timestamp": t.utc_strftime('%Y-%m-%dT%H:%M:%SZ')
        })
        
    return positions