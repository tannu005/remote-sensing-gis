"""
GIS Analysis Module - Performs Multi-Criteria Suitability Analysis
"""
import sys
from pathlib import Path
# ensure project root is on import path so 'config' can be resolved when
# running the script from the scripts/ subdirectory
sys.path.append(str(Path(__file__).parent.parent.resolve()))

import numpy as np
from config import *
import rasterio
from rasterio.features import rasterize
from rasterio.mask import mask
from scipy import ndimage
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

class SuitabilityAnalysis:
    def __init__(self):
        self.lulc_raster = None
        self.population_raster = None
        self.dem_raster = None
        self.hazard_raster = None
        self.transform = None
        self.crs = None
        self.results = {}
        
    def load_rasters(self):
        """Load all raster datasets"""
        print("Loading raster datasets...")
        
        with rasterio.open(PROCESSED_DATA_DIR / OUTPUT_FILES['lulc_raster']) as src:
            self.lulc_raster = src.read(1)
            self.transform = src.transform
            self.crs = src.crs
        
        with rasterio.open(PROCESSED_DATA_DIR / OUTPUT_FILES['population_raster']) as src:
            self.population_raster = src.read(1)
        
        with rasterio.open(PROCESSED_DATA_DIR / 'dem.tif') as src:
            self.dem_raster = src.read(1)
        
        with rasterio.open(PROCESSED_DATA_DIR / OUTPUT_FILES['hazard_raster']) as src:
            self.hazard_raster = src.read(1)
        
        print("✓ Rasters loaded")
    
    def load_shapefiles(self):
        """Load vector datasets"""
        print("Loading vector datasets...")
        
        self.roads_gdf = gpd.read_file(RAW_DATA_DIR / 'road_network.shp')
        self.schools_gdf = gpd.read_file(RAW_DATA_DIR / 'existing_schools.shp')
        self.water_gdf = gpd.read_file(RAW_DATA_DIR / 'water_bodies.shp')
        
        print("✓ Vector datasets loaded")
    
    def calculate_lulc_suitability(self):
        """Calculate suitability from LULC classification"""
        print("Calculating LULC suitability...")
        
        lulc_suitability = np.zeros_like(self.lulc_raster, dtype=np.float32)
        
        for lulc_class, score in LULC_SUITABILITY.items():
            lulc_suitability[self.lulc_raster == self.lulc_raster] = (
                score if self.lulc_raster.max() > 0 else 50
            )
        
        # Normalize to 0-100
        lulc_suitability = np.interp(
            np.arange(1, 7),
            np.arange(1, 7),
            np.array([LULC_SUITABILITY.get(f'class_{i}', 50) for i in range(1, 7)])
        )
        
        # Simplified: use actual values
        lulc_suitability = np.zeros_like(self.lulc_raster, dtype=np.float32)
        for i, (lulc_class, score) in enumerate(LULC_SUITABILITY.items(), 1):
            lulc_suitability[self.lulc_raster == i] = score
        
        self.results['lulc_suitability'] = lulc_suitability
        print("✓ LULC suitability calculated")
        return lulc_suitability
    
    def calculate_population_suitability(self):
        """Calculate suitability from population density"""
        print("Calculating population density suitability...")
        
        # Normalize population density (higher demand = higher suitability, but diminishing returns)
        pop_normalized = np.clip(self.population_raster / self.population_raster.max(), 0, 1)
        pop_suitability = 100 * (1 - np.exp(-2 * pop_normalized))  # Sigmoid curve
        
        self.results['population_suitability'] = pop_suitability
        print("✓ Population suitability calculated")
        return pop_suitability
    
    def calculate_slope_suitability(self):
        """Calculate slope suitability from DEM"""
        print("Calculating slope suitability...")
        
        # Calculate slope using Sobel filter
        sx = ndimage.sobel(self.dem_raster, axis=0)
        sy = ndimage.sobel(self.dem_raster, axis=1)
        slope_degrees = np.degrees(np.arctan(np.sqrt(sx**2 + sy**2)))
        
        slope_suitability = np.zeros_like(slope_degrees, dtype=np.float32)
        
        # Apply slope thresholds
        slope_suitability[(slope_degrees >= 0) & (slope_degrees <= 2)] = 100
        slope_suitability[(slope_degrees > 2) & (slope_degrees <= 5)] = 90
        slope_suitability[(slope_degrees > 5) & (slope_degrees <= 15)] = 70
        slope_suitability[(slope_degrees > 15) & (slope_degrees <= 30)] = 30
        slope_suitability[slope_degrees > 30] = 0
        
        self.results['slope_suitability'] = slope_suitability
        print("✓ Slope suitability calculated")
        return slope_suitability
    
    def calculate_distance_suitability(self, shapefile_path, buffer_distance, inverse=False):
        """Calculate suitability based on distance to features"""
        print(f"Calculating distance suitability from {shapefile_path.name}...")
        
        gdf = gpd.read_file(shapefile_path)
        
        # Create a raster from geometries
        shapes = [(geom, 1) for geom in gdf.geometry]
        
        height, width = self.lulc_raster.shape
        distance_raster = np.zeros((height, width), dtype=np.float32)
        
        # Calculate minimum distance from each cell to geometry
        for geom in gdf.geometry:
            for i in range(height):
                for j in range(width):
                    point = Point(
                        self.transform.c + j * self.transform.a,
                        self.transform.f + i * self.transform.e
                    )
                    dist = point.distance(geom)
                    distance_raster[i, j] = min(distance_raster[i, j] or float('inf'), dist)
        
        if inverse:
            # For schools: closer = less suitable (avoid redundancy)
            distance_suitability = np.clip(
                100 * (distance_raster / (buffer_distance * 2)), 0, 100
            )
        else:
            # For roads: closer = more suitable (accessibility)
            distance_suitability = 100 * np.exp(-distance_raster / (buffer_distance / 2))
        
        print(f"✓ Distance suitability calculated")
        return distance_suitability
    
    def calculate_hazard_avoidance(self):
        """Calculate hazard avoidance suitability"""
        print("Calculating hazard avoidance suitability...")
        
        # Hazard zones should have 0 suitability
        hazard_suitability = (1 - self.hazard_raster.astype(np.float32)) * 100
        
        self.results['hazard_suitability'] = hazard_suitability
        print("✓ Hazard avoidance calculated")
        return hazard_suitability
    
    def combine_criteria(self):
        """Combine all criteria using weighted overlay"""
        print("\nCombining criteria using weighted overlay...")
        
        height, width = self.lulc_raster.shape
        combined_suitability = np.zeros((height, width), dtype=np.float32)
        
        # Calculate individual criteria
        lulc_suit = self.calculate_lulc_suitability()
        pop_suit = self.calculate_population_suitability()
        slope_suit = self.calculate_slope_suitability()
        hazard_suit = self.calculate_hazard_avoidance()
        
        # Distance-based criteria with spatial processing
        try:
            distance_roads = self.calculate_distance_suitability(
                RAW_DATA_DIR / 'road_network.shp',
                BUFFERS['road_accessibility'],
                inverse=False
            )
            self.results['road_distance_suitability'] = distance_roads
        except:
            print("  ⚠ Road distance calculation skipped")
            distance_roads = np.ones((height, width), dtype=np.float32) * 50
        
        try:
            distance_schools = self.calculate_distance_suitability(
                RAW_DATA_DIR / 'existing_schools.shp',
                BUFFERS['school_buffer'],
                inverse=True
            )
            self.results['school_distance_suitability'] = distance_schools
        except:
            print("  ⚠ School distance calculation skipped")
            distance_schools = np.ones((height, width), dtype=np.float32) * 50
        
        try:
            distance_water = self.calculate_distance_suitability(
                RAW_DATA_DIR / 'water_bodies.shp',
                BUFFERS['water_buffer'],
                inverse=True
            )
            self.results['water_distance_suitability'] = distance_water
        except:
            print("  ⚠ Water distance calculation skipped")
            distance_water = np.ones((height, width), dtype=np.float32) * 50
        
        # Weighted combination
        combined_suitability = (
            CRITERIA_WEIGHTS['lulc_suitable'] * lulc_suit +
            CRITERIA_WEIGHTS['population_density'] * pop_suit +
            CRITERIA_WEIGHTS['distance_from_roads'] * distance_roads +
            CRITERIA_WEIGHTS['distance_from_schools'] * distance_schools +
            CRITERIA_WEIGHTS['distance_from_water'] * distance_water +
            CRITERIA_WEIGHTS['slope_suitability'] * slope_suit +
            CRITERIA_WEIGHTS['hazard_zones'] * hazard_suit
        )
        
        # Normalize
        combined_suitability = np.clip(combined_suitability, 0, 100)
        
        self.results['combined_suitability'] = combined_suitability
        print("✓ Weighted overlay completed")
        return combined_suitability
    
    def classify_suitability(self, suitability_map):
        """Classify suitability into categories"""
        print("Classifying suitability map...")
        
        classified = np.zeros_like(suitability_map, dtype=np.uint8)
        
        for class_idx, (class_name, (min_val, max_val, color)) in enumerate(
            SUITABILITY_CLASSES.items(), 1
        ):
            mask = (suitability_map >= min_val) & (suitability_map < max_val)
            classified[mask] = class_idx
        
        self.results['classified_suitability'] = classified
        print("✓ Classification completed")
        return classified
    
    def save_results(self):
        """Save all results to GeoTIFF files"""
        print("\nSaving results...")
        
        # Save continuous suitability map
        self.save_raster(
            self.results['combined_suitability'],
            OUTPUTS_DIR / OUTPUT_FILES['suitability_map']
        )
        
        # Save classified map
        self.save_raster(
            self.results['classified_suitability'],
            OUTPUTS_DIR / OUTPUT_FILES['suitability_classified']
        )
        
        # Save intermediate layers
        self.save_raster(
            self.results['lulc_suitability'],
            OUTPUTS_DIR / 'lulc_suitability.tif'
        )
        
        self.save_raster(
            self.results['population_suitability'],
            OUTPUTS_DIR / 'population_suitability.tif'
        )
        
        self.save_raster(
            self.results['slope_suitability'],
            OUTPUTS_DIR / 'slope_suitability.tif'
        )
        
        print(f"✓ Results saved to {OUTPUTS_DIR}")
    
    def save_raster(self, data, output_path):
        """Save numpy array as GeoTIFF"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with rasterio.open(
            output_path, 'w',
            driver='GTiff',
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs=self.crs,
            transform=self.transform
        ) as dst:
            dst.write(data, 1)
        
        print(f"  ✓ Saved: {output_path.name}")
    
    def generate_report(self):
        """Generate analysis report"""
        print("\nGenerating report...")
        
        report = f"""
{'='*70}
SITE SUITABILITY ANALYSIS REPORT
High School Location Selection in Chennai
{'='*70}

ANALYSIS PARAMETERS:
{'-'*70}
Study Area: Chennai, India
Resolution: {RASTER_RESOLUTION} meters
Coordinate System: {CRS}

CRITERIA WEIGHTS:
{'-'*70}
"""
        for criterion, weight in CRITERIA_WEIGHTS.items():
            report += f"  {criterion.replace('_', ' ').title()}: {weight*100:.1f}%\n"
        
        suitability_map = self.results['combined_suitability']
        
        report += f"""
SUITABILITY STATISTICS:
{'-'*70}
Minimum Suitability Score: {suitability_map.min():.2f}
Maximum Suitability Score: {suitability_map.max():.2f}
Mean Suitability Score: {suitability_map.mean():.2f}
Median Suitability Score: {np.median(suitability_map):.2f}
Standard Deviation: {suitability_map.std():.2f}

CLASSIFICATION BREAKDOWN:
{'-'*70}
"""
        
        classified = self.results['classified_suitability']
        for class_idx, (class_name, (min_val, max_val, color)) in enumerate(
            SUITABILITY_CLASSES.items(), 1
        ):
            count = np.sum(classified == class_idx)
            percentage = (count / classified.size) * 100
            report += f"  {class_name.replace('_', ' ').title()}: {count} cells ({percentage:.2f}%)\n"
        
        report += f"""
OUTPUT FILES GENERATED:
{'-'*70}
  - Suitability Map (Continuous): {OUTPUT_FILES['suitability_map']}
  - Classified Suitability Map: {OUTPUT_FILES['suitability_classified']}
  - LULC Suitability: lulc_suitability.tif
  - Population Suitability: population_suitability.tif
  - Slope Suitability: slope_suitability.tif

RECOMMENDATIONS:
{'-'*70}
1. Focus site selection on highly suitable areas (85-100 score)
2. Avoid areas marked as "not_suitable" due to hazards or constraints
3. Consider accessibility, land availability, and infrastructure
4. Validate recommended sites through field surveys
5. Consult with local authorities for final approvals

NEXT STEPS:
{'-'*70}
1. Identify top candidate locations from the suitability map
2. Conduct environmental and social impact assessments
3. Perform stakeholder consultations
4. Finalize site selection through multi-criteria decision analysis

{'='*70}
"""
        
        report_path = REPORTS_DIR / 'suitability_analysis_report.txt'
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(report)
        print(f"✓ Report saved: {report_path}")
    
    def run_full_analysis(self):
        """Execute complete analysis pipeline"""
        print("\n" + "="*70)
        print("EXECUTING SITE SUITABILITY ANALYSIS PIPELINE")
        print("="*70 + "\n")
        
        self.load_rasters()
        self.load_shapefiles()
        suitability_map = self.combine_criteria()
        classified_map = self.classify_suitability(suitability_map)
        self.save_results()
        self.generate_report()
        
        print("\n✓ Analysis complete!")
        return suitability_map, classified_map

def main():
    analysis = SuitabilityAnalysis()
    analysis.run_full_analysis()

if __name__ == "__main__":
    main()



import matplotlib.pyplot as plt
import rasterio

with rasterio.open("outputs/suitability_map.tif") as src:
    data = src.read(1)

plt.figure(figsize=(10,8))
plt.imshow(data, cmap="RdYlGn")
plt.colorbar(label="Suitability Score")
plt.title("School Site Suitability Map - Chennai")
plt.show()

