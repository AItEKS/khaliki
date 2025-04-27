import math

def calculate_satellite_coverage(
    ground_altitude_m: float,
    min_elevation_deg: float,
    satellite_altitude_km: float,
    earth_radius_km: float = 6371.0
) -> float:
    """
    Рассчитывает радиус зоны покрытия спутника (в км) от подспутниковой точки до границы видимости.

    Параметры:
        ground_altitude_m: Высота наземной станции над уровнем моря (в метрах)
        min_elevation_deg: Минимальный угол возвышения (в градусах)
        satellite_altitude_km: Высота орбиты спутника (в километрах)
        earth_radius_km: Радиус Земли (по умолчанию 6371 км)

    Возвращает:
        Радиус зоны покрытия в километрах. 0 если спутник не виден.
    """
    # Переводим высоту станции в километры
    h = ground_altitude_m / 1000  
    
    # Переводим угол возвышения в радианы
    e = math.radians(min_elevation_deg)  
    print(e,"e")
    
    # Вычисляем ключевой параметр
    ratio = (earth_radius_km + h) / (earth_radius_km + satellite_altitude_km) * math.cos(e)
    print(ratio,h)
    # Проверка на видимость спутника
    if ratio > 1:
        return 0.0
    
    # Вычисляем центральный угол
    central_angle = math.acos(ratio) - e
    print(central_angle)
    # Рассчитываем радиус покрытия
    coverage_radius = earth_radius_km * central_angle
    
    return coverage_radius


