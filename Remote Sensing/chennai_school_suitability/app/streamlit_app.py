"""
Interactive Web Application for Site Suitability Analysis
Built with Streamlit and Folium
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OUTPUTS_DIR, SUITABILITY_CLASSES, CHENNAI_BOUNDS
import matplotlib
import streamlit as st
import folium
from streamlit_folium import st_folium
import rasterio
from rasterio.plot import show
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from config import OUTPUTS_DIR, SUITABILITY_CLASSES, CHENNAI_BOUNDS
import json


st.set_page_config(
    page_title="School Site Suitability Analysis - Chennai",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_suitability_raster():
    """Load the suitability map"""
    raster_path = OUTPUTS_DIR / 'suitability_map.tif'
    if raster_path.exists():
        with rasterio.open(raster_path) as src:
            data = src.read(1)
            bounds = src.bounds
            transform = src.transform
        return data, bounds, transform
    return None, None, None

@st.cache_resource
def load_classified_raster():
    """Load the classified suitability map"""
    raster_path = OUTPUTS_DIR / 'suitability_classified.tif'
    if raster_path.exists():
        with rasterio.open(raster_path) as src:
            data = src.read(1)
        return data
    return None

@st.cache_resource
def load_existing_schools():
    """Load existing schools"""
    try:
        gdf = gpd.read_file(Path('data') / 'raw' / 'existing_schools.shp')
        return gdf
    except:
        return None

def create_folium_map():
    """Create an interactive Folium map"""
    center_lat = (CHENNAI_BOUNDS['north'] + CHENNAI_BOUNDS['south']) / 2
    center_lon = (CHENNAI_BOUNDS['east'] + CHENNAI_BOUNDS['west']) / 2
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="OpenStreetMap"
    )
    
    # Add suitability color overlay
    data, bounds, _ = load_suitability_raster()
    if data is not None:
        # Normalize for visualization
        data_norm = (data - data.min()) / (data.max() - data.min())
        
        # Add raster as image overlay (simplified)
        from rasterio.plot import show
        img = data_norm
        
        # Add schools if available
        schools = load_existing_schools()
        if schools is not None:
            for idx, row in schools.iterrows():
                folium.CircleMarker(
                    location=[row.geometry.y, row.geometry.x],
                    radius=5,
                    popup=f"School: {row['name']}",
                    color='blue',
                    fill=True,
                    fillColor='lightblue'
                ).add_to(m)
    
    return m

def display_statistics():
    """Display analysis statistics"""
    data, _, _ = load_suitability_raster()
    
    if data is not None:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Min Suitability", f"{data.min():.2f}")
        with col2:
            st.metric("Max Suitability", f"{data.max():.2f}")
        with col3:
            st.metric("Mean Suitability", f"{data.mean():.2f}")
        with col4:
            st.metric("Median Suitability", f"{np.median(data):.2f}")

def plot_suitability_histogram():
    """Plot suitability distribution"""
    data, _, _ = load_suitability_raster()
    
    if data is not None:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(data.flatten(), bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Suitability Score', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of School Site Suitability Scores (0-100)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

def plot_classification_pie():
    """Plot classification breakdown"""
    classified = load_classified_raster()
    
    if classified is not None:
        class_names = list(SUITABILITY_CLASSES.keys())
        class_counts = [np.sum(classified == i+1) for i in range(len(class_names))]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = [SUITABILITY_CLASSES[name][2] for name in class_names]
        
        wedges, texts, autotexts = ax.pie(
            class_counts,
            labels=class_names,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        ax.set_title('Suitability Classification Breakdown', fontsize=14, fontweight='bold')
        st.pyplot(fig)

def plot_suitability_map():
    """Plot the suitability map"""
    data, _, _ = load_suitability_raster()
    
    if data is not None:
        fig, ax = plt.subplots(figsize=(12, 10))
        
        im = ax.imshow(data, cmap='RdYlGn', vmin=0, vmax=100)
        ax.set_title('School Site Suitability Map - Chennai', fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitude', fontsize=11)
        ax.set_ylabel('Latitude', fontsize=11)
        
        cbar = plt.colorbar(im, ax=ax, label='Suitability Score (0-100)')
        st.pyplot(fig)

def main():
    # Header
    st.title("🏫 School Site Suitability Analysis")
    st.subheader("GIS-based Location Selection for High School - Chennai")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Select Page", [
            "Overview",
            "Suitability Map",
            "Statistics",
            "Classification",
            "Interactive Map",
            "Methodology",
            "Report"
        ])
    
    # Overview Page
    if page == "Overview":
        st.markdown("""
        ## Project Overview
        
        This application presents a GIS-based multi-criteria analysis for identifying suitable 
        locations for high school construction in Chennai.
        
        ### Key Features:
        - **Multi-Criteria Analysis**: 7 spatial criteria combined with weighted overlay
        - **Raster-Based Analysis**: Advanced GIS processing using geospatial rasters
        - **Interactive Visualization**: Explore suitability maps and statistics
        - **Data-Driven Decisions**: Science-based location recommendations
        
        ### Study Area:
        - **Location**: Chennai, Tamil Nadu, India
        - **Area**: ~6,000 sq km covering urban, peri-urban, and rural zones
        - **Population**: ~7 million
        
        ### Analysis Criteria:
        1. **LULC Suitability (20%)** - Land use classifications (buildable land)
        2. **Population Density (15%)** - Demand assessment and accessibility
        3. **Road Accessibility (15%)** - Distance to major road networks
        4. **School Redundancy (15%)** - Buffer from existing schools (avoid overlap)
        5. **Water Buffer (15%)** - Safety distance from water bodies
        6. **Slope Suitability (12%)** - Terrain feasibility for construction
        7. **Hazard Avoidance (8%)** - Flood zones and other hazards
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("📊 Total criteria analyzed: 7")
        with col2:
            st.info("🎯 Suitability scale: 0-100")
    
    # Suitability Map Page
    elif page == "Suitability Map":
        st.header("Continuous Suitability Map")
        st.markdown("Visual representation of school site suitability across the study area (0-100 scale)")
        
        plot_suitability_map()
        
        st.markdown("""
        ### Interpretation:
        - **Green areas (85-100)**: Highly suitable for school construction
        - **Yellow areas (50-85)**: Moderately to suitable areas
        - **Red areas (0-50)**: Less suitable due to constraints
        """)
    
    # Statistics Page
    elif page == "Statistics":
        st.header("Suitability Statistics")
        
        display_statistics()
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Score Distribution")
            plot_suitability_histogram()
        with col2:
            st.subheader("Area Statistics")
            data, _, _ = load_suitability_raster()
            if data is not None:
                stats_df = pd.DataFrame({
                    'Metric': ['Minimum', 'Maximum', 'Mean', 'Median', 'Std Dev'],
                    'Value': [
                        f"{data.min():.2f}",
                        f"{data.max():.2f}",
                        f"{data.mean():.2f}",
                        f"{np.median(data):.2f}",
                        f"{data.std():.2f}"
                    ]
                })
                st.dataframe(stats_df, use_container_width=True)
    
    # Classification Page
    elif page == "Classification":
        st.header("Suitability Classification")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Classification Distribution")
            plot_classification_pie()
        
        with col2:
            st.subheader("Classification Legend")
            classified = load_classified_raster()
            if classified is not None:
                class_data = []
                for class_name, (min_val, max_val, color) in SUITABILITY_CLASSES.items():
                    count = np.sum(classified == list(SUITABILITY_CLASSES.keys()).index(class_name) + 1)
                    percentage = (count / classified.size) * 100
                    class_data.append({
                        'Class': class_name.replace('_', ' ').title(),
                        'Score Range': f"{min_val}-{max_val}",
                        'Area (%)': f"{percentage:.2f}%",
                        'Count': count
                    })
                
                df = pd.DataFrame(class_data)
                st.dataframe(df, use_container_width=True)
    
    # Interactive Map Page
    elif page == "Interactive Map":
        st.header("Interactive Map")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            m = create_folium_map()
            st_folium(m, width=1200, height=600)
        with col2:
            st.markdown("""
            ### Map Features:
            - 🗺️ Base map: OpenStreetMap
            - 🏫 Blue markers: Existing schools
            - 🎨 Color overlay: Suitability zones
            - 🔍 Zoom and pan to explore
            """)
    
    # Methodology Page
    elif page == "Methodology":
        st.header("Methodology")
        
        st.markdown("""
        ## Multi-Criteria Analysis Framework
        
        ### 1. Data Preparation
        - Collection of spatial datasets (LULC, DEM, vector layers)
        - Pre-processing and standardization to common coordinate system
        - Raster conversion for uniform analysis
        
        ### 2. Criteria Evaluation
        Each criterion is converted to a suitability score (0-100):
        
        **LULC Suitability**: Assigns scores based on land use classes
        - Fallow Land: 80 (most suitable)
        - Agriculture: 70
        - Vegetation: 50
        - Water Bodies: 0 (not suitable)
        
        **Population Density**: Higher demand areas preferred
        - Uses sigmoid curve for diminishing returns
        
        **Slope Analysis**: Derived from DEM
        - 0-2°: 100 (ideal for construction)
        - 2-5°: 90
        - 5-15°: 70
        - >30°: 0 (too steep)
        
        **Accessibility**: Distance-based analysis
        - Closer to roads: Higher suitability
        - Away from existing schools: Higher suitability
        
        **Hazard Avoidance**: Constraint-based
        - Flood-prone areas: 0 suitability
        
        ### 3. Weighted Overlay
        Combined suitability = Σ(Criterion_i × Weight_i)
        
        Final score ranges from 0-100
        
        ### 4. Classification
        Results classified into 5 categories:
        - **Highly Suitable** (85-100): Best locations
        - **Suitable** (70-85): Good alternatives
        - **Moderately Suitable** (50-70): Consider with caution
        - **Less Suitable** (30-50): Alternative consideration
        - **Not Suitable** (0-30): Not recommended
        """)
    
    # Report Page
    elif page == "Report":
        st.header("Analysis Report")
        
        report_path = Path('reports') / 'suitability_analysis_report.txt'
        if report_path.exists():
            with open(report_path, 'r') as f:
                report_content = f.read()
            st.text(report_content)
        else:
            st.warning("Report not generated yet. Run the analysis first.")
        
        st.markdown("---")
        st.download_button(
            label="📥 Download Full Report",
            data=open(report_path, 'r').read() if report_path.exists() else "",
            file_name="school_suitability_report.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
