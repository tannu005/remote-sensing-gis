"""
Data Generation Module - Creates realistic spatial datasets for Chennai
"""
import sys
from pathlib import Path
# add root project directory to path so config module can be imported
sys.path.append(str(Path(__file__).parent.parent.resolve()))

import numpy as np
from config import *
import rasterio
from rasterio.transform import Affine
import geopandas as gpd
from shapely.geometry import Point, box, Polygon
import pandas as pd
from config import *

def generate_lulc_raster():
    """Generate synthetic Land Use/Land Cover raster"""
    print("Generating LULC raster...")
    
    width, height = 200, 200
    data = np.zeros((height, width), dtype=np.uint8)
    
    lulc_classes = {
        1: 'agriculture',
        2: 'fallow_land',
        3: 'built_up',
        4: 'water_body',
        5: 'vegetation',
        6: 'barren_land'
    }
    
    # Create realistic LULC pattern
    for i in range(height):
        for j in range(width):
            if i < 60:  # South - more built-up
                data[i, j] = 3 if np.random.rand() > 0.4 else np.random.choice([1, 2])
            elif i < 120:  # Middle - mixed
                data[i, j] = np.random.choice([1, 2, 5, 6])
            else:  # North - agriculture
                data[i, j] = np.random.choice([1, 2, 5], p=[0.5, 0.3, 0.2])
    
    # Add water bodies
    cv = 80
    ch = 80
    r = 15
    for i in range(height):
        for j in range(width):
            if (i - cv)**2 + (j - ch)**2 < r**2:
                data[i, j] = 4
    
    # Save raster
    transform = Affine(RASTER_RESOLUTION, 0, CHENNAI_BOUNDS['west'],
                       0, -RASTER_RESOLUTION, CHENNAI_BOUNDS['north'])
    
    output_path = PROCESSED_DATA_DIR / OUTPUT_FILES['lulc_raster']
    with rasterio.open(
        output_path, 'w',
        driver='GTiff',
        height=height, width=width,
        count=1, dtype=data.dtype,
        crs=CRS, transform=transform
    ) as dst:
        dst.write(data, 1)
    
    print(f"[OK] LULC raster saved: {output_path}")
    return output_path

def generate_population_density_raster():
    """Generate synthetic population density raster"""
    print("Generating population density raster...")
    
    width, height = 200, 200
    data = np.zeros((height, width), dtype=np.float32)
    
    # Higher density in urban areas (south)
    for i in range(height):
        for j in range(width):
            # Base gradient
            base = 1000 - (i * 3)  # Higher in south
            
            # Urban centers
            if 30 < i < 60 and 80 < j < 120:
                data[i, j] = base + np.random.normal(5000, 500)
            elif 50 < i < 80 and 60 < j < 100:
                data[i, j] = base + np.random.normal(3000, 300)
            else:
                data[i, j] = base + np.random.normal(500, 100)
            
            data[i, j] = max(0, data[i, j])
    
    transform = Affine(RASTER_RESOLUTION, 0, CHENNAI_BOUNDS['west'],
                       0, -RASTER_RESOLUTION, CHENNAI_BOUNDS['north'])
    
    output_path = PROCESSED_DATA_DIR / OUTPUT_FILES['population_raster']
    with rasterio.open(
        output_path, 'w',
        driver='GTiff',
        height=height, width=width,
        count=1, dtype=data.dtype,
        crs=CRS, transform=transform
    ) as dst:
        dst.write(data, 1)
    
    print(f"[OK] Population density raster saved: {output_path}")
    return output_path

def generate_road_network_shapefile():
    """Generate synthetic road network"""
    print("Generating road network...")
    
    roads = []
    
    # Main highways
    for j in np.linspace(79.8, 80.4, 5):
        roads.append({
            'geometry': Polygon([
                (j, CHENNAI_BOUNDS['south']),
                (j, CHENNAI_BOUNDS['north']),
                (j+0.01, CHENNAI_BOUNDS['north']),
                (j+0.01, CHENNAI_BOUNDS['south'])
            ]),
            'road_type': 'highway',
            'name': f'Highway {int(j*100)}'
        })
    
    # Local roads
    for i in range(10):
        lat = np.random.uniform(CHENNAI_BOUNDS['south'], CHENNAI_BOUNDS['north'])
        lon_start = CHENNAI_BOUNDS['west']
        lon_end = CHENNAI_BOUNDS['east']
        
        roads.append({
            'geometry': Polygon([
                (lon_start, lat),
                (lon_end, lat),
                (lon_end, lat+0.005),
                (lon_start, lat+0.005)
            ]),
            'road_type': 'local',
            'name': f'Road {i}'
        })
    
    gdf = gpd.GeoDataFrame(roads, crs=CRS)
    output_path = RAW_DATA_DIR / 'road_network.shp'
    gdf.to_file(output_path)
    
    print(f"[OK] Road network saved: {output_path}")
    return output_path

def generate_existing_schools_shapefile():
    """Generate existing schools locations"""
    print("Generating existing schools...")
    
    schools = []
    
    # Urban schools
    for i in range(15):
        lat = np.random.uniform(12.9, 13.1)
        lon = np.random.uniform(80.1, 80.3)
        schools.append({
            'geometry': Point(lon, lat),
            'school_type': np.random.choice(['primary', 'secondary']),
            'name': f'School {i+1}',
            'students': np.random.randint(200, 1000)
        })
    
    gdf = gpd.GeoDataFrame(schools, crs=CRS)
    output_path = RAW_DATA_DIR / 'existing_schools.shp'
    gdf.to_file(output_path)
    
    print(f"[OK] Existing schools saved: {output_path}")
    return output_path

def generate_water_bodies_shapefile():
    """Generate water bodies"""
    print("Generating water bodies...")
    
    water_bodies = []
    
    # Lakes/reservoirs
    water_bodies.append({
        'geometry': box(80.1, 12.95, 80.2, 13.05),
        'type': 'reservoir',
        'name': 'Red Hills Lake'
    })
    
    water_bodies.append({
        'geometry': box(80.0, 13.05, 80.15, 13.15),
        'type': 'lake',
        'name': 'Chembarambakkam Lake'
    })
    
    # Rivers
    for i in range(3):
        lon_start = 79.8 + i*0.2
        water_bodies.append({
            'geometry': Polygon([
                (lon_start, 12.8),
                (lon_start+0.3, 13.2),
                (lon_start+0.04, 13.2),
                (lon_start-0.01, 12.8)
            ]),
            'type': 'river',
            'name': f'River {i+1}'
        })
    
    gdf = gpd.GeoDataFrame(water_bodies, crs=CRS)
    output_path = RAW_DATA_DIR / 'water_bodies.shp'
    gdf.to_file(output_path)
    
    print(f"[OK] Water bodies saved: {output_path}")
    return output_path

def generate_dem_raster():
    """Generate synthetic DEM for slope calculation"""
    print("Generating DEM raster...")
    
    width, height = 200, 200
    
    # Create elevation pattern
    x = np.linspace(0, 10, width)
    y = np.linspace(0, 10, height)
    X, Y = np.meshgrid(x, y)
    
    # Combine different terrain patterns
    data = (
        100 +  # Base elevation
        20 * np.sin(X/2) +  # Gentle undulation
        15 * np.cos(Y/3) +  # Other direction
        5 * np.random.randn(height, width)  # Random noise
    ).astype(np.float32)
    
    # Add some hills
    cv, ch = 8, 8
    for i in range(height):
        for j in range(width):
            dist = np.sqrt((i/20 - cv/20)**2 + (j/20 - ch/20)**2)
            if dist < 2:
                data[i, j] += 30 * np.exp(-dist**2 / 2)
    
    transform = Affine(RASTER_RESOLUTION, 0, CHENNAI_BOUNDS['west'],
                       0, -RASTER_RESOLUTION, CHENNAI_BOUNDS['north'])
    
    output_path = PROCESSED_DATA_DIR / 'dem.tif'
    with rasterio.open(
        output_path, 'w',
        driver='GTiff',
        height=height, width=width,
        count=1, dtype=data.dtype,
        crs=CRS, transform=transform
    ) as dst:
        dst.write(data, 1)
    
    print(f"[OK] DEM raster saved: {output_path}")
    return output_path

def generate_flood_hazard_raster():
    """Generate synthetic flood hazard zones"""
    print("Generating flood hazard zones...")
    
    width, height = 200, 200
    data = np.zeros((height, width), dtype=np.uint8)
    
    # High hazard near water bodies (lower elevation areas)
    for i in range(height):
        for j in range(width):
            # Simulate lower elevation in certain areas
            if i > 140 or (80 < i < 120 and 80 < j < 120):
                hazard_prob = 0.7
            elif i > 100:
                hazard_prob = 0.4
            else:
                hazard_prob = 0.1
            
            data[i, j] = 1 if np.random.rand() < hazard_prob else 0
    
    transform = Affine(RASTER_RESOLUTION, 0, CHENNAI_BOUNDS['west'],
                       0, -RASTER_RESOLUTION, CHENNAI_BOUNDS['north'])
    
    output_path = PROCESSED_DATA_DIR / OUTPUT_FILES['hazard_raster']
    with rasterio.open(
        output_path, 'w',
        driver='GTiff',
        height=height, width=width,
        count=1, dtype=data.dtype,
        crs=CRS, transform=transform
    ) as dst:
        dst.write(data, 1)
    
    print(f"[OK] Flood hazard raster saved: {output_path}")
    return output_path

def generate_all_data():
    """Generate all spatial datasets"""
    print("\n" + "="*60)
    print("GENERATING SYNTHETIC SPATIAL DATA FOR CHENNAI")
    print("="*60 + "\n")
    
    generate_lulc_raster()
    generate_population_density_raster()
    generate_dem_raster()
    generate_flood_hazard_raster()
    generate_road_network_shapefile()
    generate_existing_schools_shapefile()
    generate_water_bodies_shapefile()
    
    print("\n[OK] All datasets generated successfully!")
    print(f"Raw data location: {RAW_DATA_DIR}")
    print(f"Processed data location: {PROCESSED_DATA_DIR}\n")

if __name__ == "__main__":
    generate_all_data()
