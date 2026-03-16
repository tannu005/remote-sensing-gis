# School Site Suitability Analysis for Chennai - Complete GIS Project

## Project Overview

This is a **comprehensive, professional-grade GIS project** for identifying suitable locations for high school construction in Chennai using **raster-based multi-criteria analysis**. The project demonstrates advanced GIS techniques, spatial analysis, and data-driven decision-making.

### Key Features

✨ **Advanced GIS Capabilities**:
- Multi-criteria suitability analysis with weighted overlay
- Raster-based spatial analysis (30m resolution)
- Distance analysis and buffer operations
- Terrain derivative calculations (slope from DEM)
- Classification and zoning analysis
- Statistical spatial analysis

🛠️ **Complete Technology Stack**:
- **Data Processing**: GeoPandas, Rasterio, Fiona
- **Analysis**: SciPy, NumPy, Scikit-image
- **Visualization**: Matplotlib, Seaborn, Folium
- **Web Application**: Streamlit with interactive maps
- **Analysis Tools**: Jupyter Notebooks
- **Geospatial**: GDAL, Shapely, PyProj

📊 **Workflows Included**:
- Synthetic realistic data generation
- Full GIS analysis pipeline
- Interactive web dashboard
- Statistical reporting
- Publication-ready visualizations

---

## Project Structure

```
chennai_school_suitability/
├── data/
│   ├── raw/                    # Vector datasets (shapefiles)
│   │   ├── road_network.shp
│   │   ├── existing_schools.shp
│   │   ├── water_bodies.shp
│   │   └── ...
│   └── processed/              # Raster datasets (GeoTIFFs)
│       ├── lulc_raster.tif
│       ├── population_raster.tif
│       ├── dem.tif
│       ├── hazard_zones.tif
│       └── ...
├── scripts/
│   ├── data_generation.py      # Generate synthetic spatial data
│   └── gis_analysis.py         # Multi-criteria suitability analysis
├── notebooks/
│   └── 01_School_Suitability_Analysis.ipynb  # Detailed analysis notebook
├── app/
│   └── streamlit_app.py        # Interactive web dashboard
├── outputs/                     # Analysis results
│   ├── suitability_map.tif
│   ├── suitability_classified.tif
│   ├── *.png                   # Visualizations
│   └── ...
├── reports/                     # Generated reports
│   └── suitability_analysis_report.txt
├── config.py                    # Project configuration
├── requirements.txt             # Python dependencies
├── run_analysis.py             # Main execution script
└── README.md                    # This file
```

---

## Installation and Setup

### Prerequisites
- Python 3.8 through 3.12 (Python 3.13 is **not** currently supported due to lack of NumPy/ scientific package wheels)
- Windows, macOS, or Linux
- ~500MB disk space for data and outputs

### Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd "C:\Users\psk26\Remote Sensing\chennai_school_suitability"

# Create virtual environment
python -m venv venv

# Activate environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python -c "import geopandas, rasterio, streamlit; print('✓ All packages installed')"
```

---

## Quick Start

### Option 1: Run Full Analysis Pipeline

```bash
python run_analysis.py
```

This will:
1. Generate synthetic spatial data
2. Perform complete GIS analysis
3. Create suitability maps
4. Generate statistical report
5. Save all outputs

**Time**: ~2-5 minutes

### Option 2: Run Jupyter Notebook

```bash
jupyter notebook notebooks/01_School_Suitability_Analysis.ipynb
```

Interactive analysis with detailed explanations and visualizations.

### Option 3: Launch Interactive Dashboard

```bash
streamlit run app/streamlit_app.py
```

Open browser to `http://localhost:8501` for interactive visualization.

---

## Analysis Methodology

### Multi-Criteria Analysis Framework

The project uses **weighted overlay analysis** combining 7 spatial criteria:

| Criterion | Weight | Description | Data Source |
|-----------|--------|-------------|-------------|
| LULC Suitability | 20% | Identify buildable land types | Classified LULC raster |
| Population Density | 15% | Assess demand and accessibility | Population distribution |
| Road Accessibility | 15% | Distance to transporation network | Road network shapefile |
| School Redundancy | 15% | Avoid existing school coverage | Existing schools shapefile |
| Water Buffer | 15% | Safety distance from water bodies | Water bodies shapefile |
| Slope Suitability | 12% | Construction feasibility | DEM-derived slope |
| Hazard Avoidance | 8% | Avoid flood-prone areas | Hazard zones |

**Total**: 100% (weighted average)

### Processing Steps

1. **Data Preparation**
   - Load raster and vector datasets
   - Standardize to common CRS (EPSG:4326)
   - Normalize to 30m resolution grid

2. **Criteria Evaluation**
   - Calculate suitability score (0-100) for each criterion
   - Apply thresholds and distance decay functions
   - Handle constraints and buffers

3. **Weighted Overlay**
   - Combine all criteria using predetermined weights
   - Generate continuous suitability map (0-100)

4. **Classification**
   - Group suitability scores into 5 categories
   - Generate classified zoning map

5. **Validation & Reporting**
   - Calculate area statistics
   - Generate visualizations
   - Produce recommendations

---

## Key Analysis Outputs

### 1. Suitability Map (Continuous)
- **File**: `suitability_map.tif`
- **Format**: GeoTIFF, 32-bit float
- **Values**: 0-100 (suitability score)
- **Resolution**: 30 meters

### 2. Classified Suitability Map
- **File**: `suitability_classified.tif`
- **Format**: GeoTIFF, 8-bit integer
- **Categories**:
  - 1: Not Suitable (0-30)
  - 2: Less Suitable (30-50)
  - 3: Moderately Suitable (50-70)
  - 4: Suitable (70-85)
  - 5: Highly Suitable (85-100)

### 3. Intermediate Layer Maps
Each criterion saved separately for detailed analysis:
- `lulc_suitability.tif` - Land use classification
- `population_suitability.tif` - Population-based scores
- `slope_suitability.tif` - Terrain classification
- And more...

### 4. Visualizations
- Distribution histograms
- Classification pie charts
- Multi-layer comparison maps
- Statistical plots

### 5. Reports
- `suitability_analysis_report.txt` - Summary statistics and recommendations

---

## Data Sources and Parameters

### Input Datasets
The project generates **synthetic realistic data** for demonstration:

1. **LULC Classification**: 6 classes (agriculture, urban, water, etc.)
2. **Population Density**: Realistic distribution with urban centers
3. **DEM**: Synthetic elevation with terrain variations
4. **Road Network**: Major highways and local roads
5. **Existing Schools**: Sample school locations
6. **Water Bodies**: Lakes, rivers, reservoirs
7. **Hazard Zones**: Flood-prone areas

### Configuration Parameters (config.py)

```python
# Study Area
CHENNAI_BOUNDS = {
    'north': 13.3, 'south': 12.8,
    'east': 80.4, 'west': 79.8
}

# Analysis Resolution
RASTER_RESOLUTION = 30  # meters

# Suitability Weights
CRITERIA_WEIGHTS = {
    'lulc_suitable': 0.20,
    'population_density': 0.15,
    'distance_from_roads': 0.15,
    'distance_from_schools': 0.15,
    'distance_from_water': 0.15,
    'slope_suitability': 0.12,
    'hazard_zones': 0.08
}

# Safety Buffers
BUFFERS = {
    'school_buffer': 500,      # meters
    'water_buffer': 200,       # meters
    'road_accessibility': 2000  # meters
}
```

### Customization

Edit `config.py` to:
- Change study area bounds
- Adjust criteria weights
- Modify buffer distances
- Update LULC suitability scores
- Change slope thresholds

---

## Analysis Results Interpretation

### Suitability Scores

| Score | Category | Interpretation |
|-------|----------|-----------------|
| 85-100 | **Highly Suitable** | Excellent locations, prioritize |
| 70-85 | **Suitable** | Good alternatives |
| 50-70 | **Moderately Suitable** | Consider with caution |
| 30-50 | **Less Suitable** | Limited suitability |
| 0-30 | **Not Suitable** | Avoid these areas |

### Area Statistics
The report provides:
- Total area in each suitability class
- Percentage coverage
- Pixel counts
- Statistical measures (mean, median, std dev)

### Map Interpretation

**Green areas** (high suitability):
- Better land use compatibility
- Good population demand
- High accessibility
- Far from constraints

**Red areas** (low suitability):
- Water bodies or hazard zones
- Poor terrain (too steep)
- Existing school coverage
- Limited accessibility

---

## Advanced Usage

### 1. Modify Analysis Weights

Edit `config.py`:
```python
CRITERIA_WEIGHTS = {
    'lulc_suitable': 0.25,      # Increase importance
    'population_density': 0.10,  # Decrease importance
    # ... other criteria
}
```

### 2. Change Study Area

```python
CHENNAI_BOUNDS = {
    'north': 13.5,
    'south': 12.5,
    'east': 80.5,
    'west': 79.5
}
```

### 3. Add New Criteria

Edit `scripts/gis_analysis.py`:
```python
def calculate_new_criterion(self):
    # Implement your analysis
    new_criterion = ...
    return new_criterion

# Add to weighted overlay:
combined_suitability = (
    # ... existing criteria ...
    0.10 * new_criterion  # 10% weight
)
```

### 4. Use Real Data

Replace synthetic data with real shapefiles/rasters:
```python
# In scripts/gis_analysis.py
self.roads_gdf = gpd.read_file('path/to/real/roads.shp')
self.schools_gdf = gpd.read_file('path/to/real/schools.shp')
```

---

## Project Applications

This framework can be adapted for:

1. **Infrastructure Planning**
   - Police stations, fire stations
   - Hospitals, clinics
   - Government buildings

2. **Urban Development**
   - Industrial zones
   - Commercial centers
   - Residential areas

3. **Environmental Management**
   - Wildlife sanctuaries
   - Landfill locations
   - Agricultural zones

4. **Disaster Management**
   - Evacuation centers
   - Relief distribution
   - Risk assessment

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'geopandas'"
**Solution**: Run `pip install -r requirements.txt`

### Issue: "No such file or directory: 'data/raw/...'"
**Solution**: Run `python run_analysis.py` first to generate data

### Issue: Streamlit app not loading
**Solution**: Check Python version (3.8+) and run from correct directory

### Issue: Rasterio/GDAL errors
**Solution**: On Windows, install binary wheels from [OSGeo4W](https://trac.osgeo.org/osgeo4w/)

---

## Performance Considerations

| Operation | Time | Memory |
|-----------|------|--------|
| Data Generation | ~10 seconds | ~200 MB |
| GIS Analysis | ~30-60 seconds | ~500 MB |
| Jupyter Notebook | Interactive | ~300 MB |
| Streamlit App | Real-time | ~400 MB |

**System Requirements**:
- CPU: Dual-core processor
- RAM: 2GB minimum, 4GB recommended
- Storage: 500MB for project
- Network: Not required (offline analysis)

---

## References and Documentation

### GIS Concepts
- [ESRI Multi-Criteria Decision Analysis](https://www.esri.com/)
- [Raster-Based Overlay Analysis](https://desktop.arcgis.com/en/arcmap/)
- [Weighted Overlay Method](https://en.wikipedia.org/wiki/Overlay_analysis)

### Python Libraries
- [GeoPandas](https://geopandas.org/)
- [Rasterio](https://rasterio.readthedocs.io/)
- [Streamlit](https://streamlit.io/)
- [Folium](https://python-visualization.github.io/folium/)

### Related Methodologies
- Multi-Criteria Decision Analysis (MCDA)
- Analytic Hierarchy Process (AHP)
- Geospatial Analysis
- Site Selection Modeling

---

## Files Guide

### Core Scripts
- **`run_analysis.py`** - Main execution script
- **`config.py`** - Configuration and parameters
- **`scripts/data_generation.py`** - Data creation
- **`scripts/gis_analysis.py`** - Analysis engine

### Notebooks & Apps
- **`notebooks/01_School_Suitability_Analysis.ipynb`** - Detailed analysis
- **`app/streamlit_app.py`** - Interactive dashboard

### Data & Outputs
- **`data/raw/`** - Input shapefiles
- **`data/processed/`** - Processed rasters
- **`outputs/`** - Analysis results
- **`reports/`** - Generated reports

---

## Future Enhancements

Potential improvements:

1. **Real Data Integration**
   - Use actual OSM data for roads
   - Download real satellite LULC
   - Use SRTM/ASTER DEM data

2. **Advanced Analysis**
   - Machine learning classification
   - Network analysis (actual travel time)
   - Multi-objective optimization

3. **Interactive Features**
   - Map-based parameter adjustment
   - Real-time weight modification
   - Dynamic scenario analysis

4. **Validation**
   - Stakeholder feedback integration
   - Ground truth comparison
   - Accuracy assessment

---

## License and Usage

This project is provided as an educational and professional reference for GIS analysis. It demonstrates best practices in:
- Spatial data processing
- Multi-criteria analysis
- Raster-based GIS workflows
- Professional documentation

---

## Support and Contact

For questions or issues:
1. Check troubleshooting section
2. Review Jupyter notebook comments
3. Examine config.py for parameter details
4. Consult referenced GIS documentation

---

## Authors

**Project Type**: Educational/Professional GIS Analysis
**Version**: 1.0
**Last Updated**: 2026

---

**Ready to start? Run `python run_analysis.py` to begin!**

---
