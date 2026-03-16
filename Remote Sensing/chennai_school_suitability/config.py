"""
Configuration file for Site Suitability Analysis Project - Chennai
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = PROJECT_ROOT / "reports"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUTS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Chennai study area bounds (lat, lon)
CHENNAI_BOUNDS = {
    'north': 13.3,
    'south': 12.8,
    'east': 80.4,
    'west': 79.8
}

# Raster parameters
RASTER_RESOLUTION = 30  # meters
CRS = "EPSG:4326"  # WGS84

# Suitability criteria weights (sum = 100)
CRITERIA_WEIGHTS = {
    'lulc_suitable': 0.20,           # 20% - Land use suitability
    'population_density': 0.15,      # 15% - Population accessibility
    'distance_from_roads': 0.15,     # 15% - Road accessibility
    'distance_from_schools': 0.15,   # 15% - Avoid redundancy
    'distance_from_water': 0.15,     # 15% - Safety buffer
    'slope_suitability': 0.12,       # 12% - Construction feasibility
    'hazard_zones': 0.08            # 8% - Hazard avoidance (flood, etc.)
}

# LULC class suitability scores (0-100)
LULC_SUITABILITY = {
    'agriculture': 70,
    'fallow_land': 80,
    'built_up': 30,
    'water_body': 0,
    'vegetation': 50,
    'barren_land': 60,
    'other': 40
}

# Slope suitability (degree-based)
SLOPE_SUITABILITY = {
    'flat': (0, 2, 100),          # (min, max, score)
    'gentle': (2, 5, 90),
    'moderate': (5, 15, 70),
    'steep': (15, 30, 30),
    'very_steep': (30, 90, 0)
}

# Distance buffers (meters)
BUFFERS = {
    'school_buffer': 500,      # Min 500m from existing schools
    'water_buffer': 200,       # Min 200m from water bodies
    'road_accessibility': 2000  # Max 2km from roads
}

# Output file names
OUTPUT_FILES = {
    'lulc_raster': 'lulc_raster.tif',
    'population_raster': 'population_raster.tif',
    'road_distance': 'distance_from_roads.tif',
    'school_distance': 'distance_from_schools.tif',
    'water_distance': 'distance_from_water.tif',
    'slope_raster': 'slope_raster.tif',
    'hazard_raster': 'hazard_zones.tif',
    'suitability_map': 'suitability_map.tif',
    'suitability_classified': 'suitability_classified.tif'
}

# Classification thresholds
SUITABILITY_CLASSES = {
    'not_suitable': (0, 30, '#d73027'),
    'less_suitable': (30, 50, '#fee090'),
    'moderately_suitable': (50, 70, '#ffffbf'),
    'suitable': (70, 85, '#e0f3f8'),
    'highly_suitable': (85, 100, '#91bfdb')
}

print("[OK] Configuration loaded for Chennai Site Suitability Analysis")
