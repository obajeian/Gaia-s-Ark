import numpy as np
import math
from typing import Tuple, List

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth in kilometers"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def calculate_ndvi_proxy(biomass_density: float) -> float:
    """Calculate NDVI proxy from biomass density"""
    # Normalize biomass density to NDVI range (0-1)
    normalized = min(1.0, max(0.0, biomass_density / 300))
    return round(normalized, 3)

def estimate_canopy_coverage(mangrove_area: float, biomass_density: float) -> float:
    """Estimate canopy coverage percentage"""
    # Higher biomass density indicates denser canopy
    base_coverage = min(95, biomass_density / 2.5)
    area_factor = min(1.2, math.log(mangrove_area + 1) / 3)
    
    coverage = base_coverage * area_factor
    return round(min(95, max(10, coverage)), 1)

def get_coastal_zone(latitude: float, longitude: float) -> str:
    """Determine coastal zone based on coordinates"""
    # Kenya coastal zones
    if -2.5 <= latitude <= -2.0:
        return "Northern Coast"
    elif -3.0 <= latitude <= -2.5:
        return "Central Coast"
    elif -4.0 <= latitude <= -3.0:
        return "Mombasa Region"
    elif -4.8 <= latitude <= -4.0:
        return "Southern Coast"
    else:
        return "Unknown Zone"

def calculate_tidal_influence(latitude: float, longitude: float) -> float:
    """Calculate tidal influence factor (0-1)"""
    # Simplified tidal influence based on proximity to major tidal channels
    # Higher values indicate stronger tidal influence
    
    # Major tidal areas in Kenya coast
    tidal_centers = [
        (-2.3, 40.1),  # Lamu
        (-3.2, 40.1),  # Malindi
        (-4.0, 39.7),  # Mombasa
        (-4.4, 39.4)   # Shimoni
    ]
    
    min_distance = min(
        haversine_distance(latitude, longitude, lat, lon)
        for lat, lon in tidal_centers
    )
    
    # Convert distance to influence factor (closer = higher influence)
    influence = max(0.1, 1.0 - (min_distance / 50))
    return round(influence, 3)

def generate_grid_points(bounds: Tuple[float, float, float, float], resolution: float = 0.01) -> List[Tuple[float, float]]:
    """Generate grid points within given bounds"""
    min_lat, min_lon, max_lat, max_lon = bounds
    
    points = []
    lat = min_lat
    while lat <= max_lat:
        lon = min_lon
        while lon <= max_lon:
            points.append((lat, lon))
            lon += resolution
        lat += resolution
    
    return points

def calculate_area_hectares(polygon_coords: List[Tuple[float, float]]) -> float:
    """Calculate area of polygon in hectares using shoelace formula"""
    if len(polygon_coords) < 3:
        return 0.0
    
    # Convert to meters (approximate)
    coords_m = []
    for lat, lon in polygon_coords:
        x = lon * 111320 * math.cos(math.radians(lat))
        y = lat * 110540
        coords_m.append((x, y))
    
    # Shoelace formula
    area = 0.0
    n = len(coords_m)
    for i in range(n):
        j = (i + 1) % n
        area += coords_m[i][0] * coords_m[j][1]
        area -= coords_m[j][0] * coords_m[i][1]
    
    area = abs(area) / 2.0
    return area / 10000  # Convert m² to hectares