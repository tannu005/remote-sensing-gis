# 🛰️ School Site Suitability Analysis — India GIS

> **Multi-Criteria GIS Analysis for High School Location Selection across all Indian States & Cities**  
> Built during the **India Space Lab (ISL) Winter Internship Technical Training Program 2026**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://remote-sensing-gis-ftk4znsyyftydvmnng7iwh.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)
![OpenStreetMap](https://img.shields.io/badge/Data-OpenStreetMap-green?logo=openstreetmap)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Overview

This project implements a **Multi-Criteria Decision Analysis (MCDA)** pipeline to identify optimal locations for constructing new high schools across India. It combines real geospatial data fetched live from **OpenStreetMap**, **Census of India 2021** population statistics, and state-specific terrain and flood hazard profiles to compute a composite suitability score for every location in the selected area.

The app supports **two-level geographic analysis**:
- 🗺️ **State-level** — analyse all 28 states and 2 Union Territories
- 📌 **City-level** — drill down into specific cities with tight bounding boxes (~10×10 km) for high-resolution analysis

Originally developed as a **Pilot Project** at India Space Lab (भारत अंतरिक्ष प्रयोगशाला), a program affiliated with **NASA, JAXA, Skill India, and UN-GGIM**.

---

## 🌐 Live Demo

🔗 **[remote-sensing-gis-ftk4znsyyftydvmnng7iwh.streamlit.app](https://remote-sensing-gis-ftk4znsyyftydvmnng7iwh.streamlit.app)**

---

## ✨ Features

### 🗺️ Geographic Coverage
- **All 28 Indian States + 2 Union Territories** (Delhi, Puducherry)
- **150+ cities** with precise bounding boxes — 5 to 8 cities per state
- Switch between **entire state** or **specific city** analysis from the sidebar

### 📡 Real Data Sources
| Data | Source | Type |
|------|--------|------|
| School / College locations | OpenStreetMap Overpass API | Live fetch |
| Primary & secondary roads | OpenStreetMap Overpass API | Live fetch |
| Population, density, urbanisation | Census of India 2021 | Static registry |
| Terrain slope profile | State terrain classification | Static registry |
| Flood hazard intensity | State flood risk index | Static registry |

### 📊 Analysis & Visualisation
- **Suitability map** with real geographic coordinates (lat/lon extent)
- **White dot overlay** of existing school locations from OSM
- **Classification pie chart** — 5 suitability categories
- **Score distribution histogram** with mean/median markers
- **7 individual criterion layer maps** rendered side by side
- **Live statistics** — min, max, mean, median, std deviation
- **Dynamic methodology table** that updates with active weights

### ⚙️ Interactive Controls
- **7 adjustable weight sliders** — auto-normalised to 100%
- Weights update the analysis and all charts in real time
- State info panel — terrain type, flood risk, population tier

---

## 🔬 Methodology

### Multi-Criteria Analysis Framework

**Step 1 — Data Preparation**
- Spatial datasets collected: LULC rasters, DEM, road networks, existing school locations, water bodies, flood hazard zones
- Pre-processed and standardised to EPSG:4326 coordinate system
- Mapped to uniform 200×200 raster grid for the selected area

**Step 2 — Criteria Scoring (0–100 scale)**

| Criterion | Scoring Logic | Weight (default) |
|-----------|--------------|-----------------|
| LULC Suitability | Fallow Land: 80 · Agriculture: 70 · Vegetation: 50 · Water: 0 | 20% |
| Population Density | Sigmoid curve — higher demand preferred | 15% |
| Distance from Roads | Closer to primary/secondary roads = higher score | 15% |
| Distance from Schools | Away from existing schools = higher score | 15% |
| Distance from Water | Safe buffer from water bodies | 15% |
| Slope Suitability | 0–2°: 100 · 2–5°: 90 · 5–15°: 70 · >30°: 0 | 12% |
| Hazard Zone Avoidance | Flood-prone areas = 0 suitability | 8% |

**Step 3 — Weighted Overlay**
```
Combined Suitability = Σ (Criterion_i × Weight_i)
Final score: 0 – 100
```

**Step 4 — Classification**
| Class | Score Range | Description |
|-------|------------|-------------|
| Highly Suitable | 85–100 | Best locations for construction |
| Suitable | 70–85 | Good alternatives |
| Moderately Suitable | 50–70 | Consider with caution |
| Less Suitable | 30–50 | Not recommended |
| Not Suitable | 0–30 | Avoid — hazards or constraints |

### State-Specific Profiles
Each state has a unique profile that shapes the analysis:
- **Terrain** — mountain states (HP, Uttarakhand, Sikkim) get steep slope distributions; delta/floodplain states (West Bengal, Assam) get near-flat terrain
- **Flood hazard** — Assam (0.80), Bihar (0.75), West Bengal (0.70) generate significantly more hazard zones than Rajasthan (0.15)
- **Population** — Delhi (1.00), Uttar Pradesh (0.95) generate denser demand clusters; Arunachal Pradesh (0.05) generates sparse ones

---

## 📁 Project Structure

```
remote-sensing-gis/
├── streamlit_app.py        # Main Streamlit application
├── requirements.txt        # Python dependencies
├── Remote Sensing/         # Original project files & reports
│   ├── Project Report      # ISL internship project report (PDF)
│   └── ...
└── README.md               # This file
```

---

## 🚀 Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/tannu005/remote-sensing-gis.git
cd remote-sensing-gis
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

> **Note:** The app fetches real data from the OpenStreetMap Overpass API on load. Results are cached for 1 hour. If OSM is unreachable, the analysis falls back to simulated spatial data automatically.

---

## 📦 Dependencies

```
streamlit>=1.32.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
plotly>=5.18.0
requests>=2.31.0
```

---

## 🏙️ Supported Cities (sample)

| State | Cities |
|-------|--------|
| Tamil Nadu | Chennai, Coimbatore, Madurai, Tiruchirappalli, Salem, Tirunelveli, Vellore |
| Maharashtra | Mumbai, Pune, Nagpur, Nashik, Aurangabad, Solapur, Thane |
| Uttar Pradesh | Lucknow, Kanpur, Agra, Varanasi, Prayagraj, Meerut, Noida, Ghaziabad |
| Karnataka | Bengaluru, Mysuru, Hubli, Mangaluru, Belagavi, Davanagere |
| Rajasthan | Jaipur, Jodhpur, Udaipur, Kota, Ajmer, Bikaner |
| West Bengal | Kolkata, Howrah, Durgapur, Asansol, Siliguri, Bardhaman |
| Gujarat | Ahmedabad, Surat, Vadodara, Rajkot, Gandhinagar, Bhavnagar |
| ... | *(150+ cities across all 30 states/UTs)* |

---

## 👩‍💻 Author

**Tannu Yadav**  
B.Tech — Computer Science & Engineering  
Vellore Institute of Technology — Amravati (VIT-AP)  
Enrollment: ISL-481895

📧 ytannu1410@gmail.com  
🔗 [github.com/tannu005](https://github.com/tannu005)  
🔗 [linkedin.com/in/tannu-yadav-06012733a](https://linkedin.com/in/tannu-yadav-06012733a)

---

## 🏅 Internship

**India Space Lab (भारत अंतरिक्ष प्रयोगशाला)**  
Winter Internship Technical Training Program 2026  
📅 2nd February – 3rd March 2026

**Modules completed:**
- Advanced Drone Technology
- CanSat and CubeSat Satellite Programs
- Rocketry Science
- **Remote Sensing & GIS** ← this project
- Disaster Management

*Affiliated with NASA · JAXA · Skill India · UN-GGIM · Viksit Bharat Abhiyan*

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
🛰️ <b>India Space Lab</b> — Demonstrating excellence in Space Science and Technology
</div>
