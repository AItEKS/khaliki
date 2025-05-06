import math

def calculate_satellite_coverage(
    ground_altitude_m: float,
    min_elevation_deg: float,
    satellite_altitude_km: float,
    earth_radius_km: float = 6371.0
) -> float:
    """
    Calculates the radius of the satellite coverage area (in km) from the sub-satellite point to the visibility limit.

    Parameters:
    ground_altitude_m: Ground station altitude above sea level (in meters)
    min_elevation_deg: Minimum elevation angle (in degrees)
    satellite_altitude_km: Satellite orbit altitude (in kilometers)
    earth_radius_km: Earth radius (default 6371 km)

    Returns:
    Coverage area radius in kilometers. 0 if the satellite is not visible.
    """
    # Переводим высоту станции в километры
    ground_altitude_km = ground_altitude_m / 1000
    
    # Переводим угол возвышения в радианы
    elevation_rad = math.radians(min_elevation_deg)
    
    # Вычисляем ключевой параметр
    ratio = (earth_radius_km + ground_altitude_km) / (earth_radius_km + satellite_altitude_km) * math.cos(elevation_rad)
    
    # Проверка на видимость спутника
    if ratio > 1:
        return 0.0
        
    # Вычисляем центральный угол
    central_angle = math.acos(ratio) - elevation_rad
    
    # Рассчитываем радиус покрытия
    coverage_radius = earth_radius_km * central_angle
    
    return coverage_radius