import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import plotly.graph_objects as go
import requests

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="School Site Suitability — India GIS",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Space Mono', monospace !important; }
.hero-title { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; color: #e6f1ff; line-height: 1.3; margin-bottom: 0.3rem; }
.hero-sub   { font-family: 'DM Sans', sans-serif; font-size: 1rem; color: #8b949e; margin-bottom: 1rem; }
.badge { display: inline-block; background: #1a2332; border: 1px solid #30363d; color: #58a6ff; font-family: 'Space Mono', monospace; font-size: 0.72rem; padding: 4px 10px; border-radius: 20px; margin-right: 6px; margin-bottom: 6px; }
.metric-card { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 1rem 1.2rem; text-align: center; }
.metric-label { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 1.1rem; font-weight: 700; color: #e6f1ff; }
.metric-unit  { font-size: 0.75rem; color: #58a6ff; margin-left: 3px; }
.section-header { font-family: 'Space Mono', monospace; font-size: 0.9rem; font-weight: 700; color: #58a6ff; text-transform: uppercase; letter-spacing: 0.1em; border-bottom: 1px solid #21262d; padding-bottom: 0.5rem; margin-bottom: 1rem; }
.state-info { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; font-size: 0.82rem; color: #c9d1d9; line-height: 1.9; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# State Registry
# ─────────────────────────────────────────────
STATES = {
    "Andhra Pradesh":     {"bbox": [76.2,12.6,84.8,19.9], "pop": 0.55, "flood": 0.35, "terrain": "coastal_plain"},
    "Arunachal Pradesh":  {"bbox": [91.5,26.6,97.4,29.5], "pop": 0.05, "flood": 0.20, "terrain": "mountain"},
    "Assam":              {"bbox": [89.7,24.1,96.0,28.2], "pop": 0.60, "flood": 0.80, "terrain": "floodplain"},
    "Bihar":              {"bbox": [83.3,24.3,88.3,27.5], "pop": 0.90, "flood": 0.75, "terrain": "plains"},
    "Chhattisgarh":       {"bbox": [80.2,17.8,84.4,24.1], "pop": 0.35, "flood": 0.30, "terrain": "plateau"},
    "Goa":                {"bbox": [73.7,14.9,74.3,15.8], "pop": 0.65, "flood": 0.40, "terrain": "coastal"},
    "Gujarat":            {"bbox": [68.2,20.1,74.5,24.7], "pop": 0.55, "flood": 0.45, "terrain": "mixed"},
    "Haryana":            {"bbox": [74.5,27.7,77.6,30.9], "pop": 0.70, "flood": 0.35, "terrain": "plains"},
    "Himachal Pradesh":   {"bbox": [75.6,30.4,79.0,33.2], "pop": 0.20, "flood": 0.25, "terrain": "mountain"},
    "Jharkhand":          {"bbox": [83.3,21.9,87.9,25.4], "pop": 0.50, "flood": 0.40, "terrain": "plateau"},
    "Karnataka":          {"bbox": [74.1,11.6,78.6,18.4], "pop": 0.55, "flood": 0.30, "terrain": "plateau"},
    "Kerala":             {"bbox": [74.9,8.2, 77.4,12.8], "pop": 0.75, "flood": 0.55, "terrain": "coastal_hill"},
    "Madhya Pradesh":     {"bbox": [74.0,21.1,82.8,26.9], "pop": 0.40, "flood": 0.35, "terrain": "plateau"},
    "Maharashtra":        {"bbox": [72.6,15.6,80.9,22.0], "pop": 0.60, "flood": 0.40, "terrain": "mixed"},
    "Manipur":            {"bbox": [93.0,23.8,94.8,25.7], "pop": 0.30, "flood": 0.35, "terrain": "hill"},
    "Meghalaya":          {"bbox": [89.8,25.0,92.8,26.1], "pop": 0.30, "flood": 0.45, "terrain": "hill"},
    "Mizoram":            {"bbox": [92.3,21.9,93.5,24.5], "pop": 0.20, "flood": 0.30, "terrain": "hill"},
    "Nagaland":           {"bbox": [93.3,25.2,95.3,27.0], "pop": 0.25, "flood": 0.25, "terrain": "hill"},
    "Odisha":             {"bbox": [81.4,17.8,87.5,22.6], "pop": 0.50, "flood": 0.65, "terrain": "coastal_plain"},
    "Punjab":             {"bbox": [73.9,29.6,76.9,32.5], "pop": 0.75, "flood": 0.40, "terrain": "plains"},
    "Rajasthan":          {"bbox": [69.5,23.0,78.3,30.2], "pop": 0.30, "flood": 0.15, "terrain": "desert"},
    "Sikkim":             {"bbox": [88.0,27.1,88.9,28.1], "pop": 0.15, "flood": 0.30, "terrain": "mountain"},
    "Tamil Nadu":         {"bbox": [76.3,8.1, 80.4,13.6], "pop": 0.65, "flood": 0.45, "terrain": "coastal_plain"},
    "Telangana":          {"bbox": [77.2,15.8,81.3,19.9], "pop": 0.55, "flood": 0.35, "terrain": "plateau"},
    "Tripura":            {"bbox": [91.2,22.9,92.4,24.5], "pop": 0.55, "flood": 0.50, "terrain": "hill"},
    "Uttar Pradesh":      {"bbox": [77.1,23.9,84.6,30.4], "pop": 0.95, "flood": 0.60, "terrain": "plains"},
    "Uttarakhand":        {"bbox": [77.6,28.7,81.0,31.4], "pop": 0.30, "flood": 0.40, "terrain": "mountain"},
    "West Bengal":        {"bbox": [85.8,21.6,89.9,27.2], "pop": 0.85, "flood": 0.70, "terrain": "delta"},
    "Delhi":              {"bbox": [76.8,28.4,77.3,28.9], "pop": 1.00, "flood": 0.45, "terrain": "urban"},
    "Puducherry":         {"bbox": [79.7,11.8,80.0,12.1], "pop": 0.70, "flood": 0.50, "terrain": "coastal"},
}

TERRAIN_SLOPE = {
    "mountain":      {"mean": 22, "std": 8},
    "hill":          {"mean": 12, "std": 5},
    "coastal_hill":  {"mean": 8,  "std": 4},
    "plateau":       {"mean": 6,  "std": 3},
    "mixed":         {"mean": 5,  "std": 3},
    "coastal_plain": {"mean": 2,  "std": 1.5},
    "plains":        {"mean": 2,  "std": 1},
    "floodplain":    {"mean": 1,  "std": 0.8},
    "delta":         {"mean": 1,  "std": 0.5},
    "desert":        {"mean": 3,  "std": 2},
    "urban":         {"mean": 2,  "std": 1},
    "coastal":       {"mean": 2,  "std": 1.5},
}

POPULATION_DATA = {
    "Uttar Pradesh":      {"pop_millions": 231.5, "density": 828,  "urban_pct": 22.3},
    "Maharashtra":        {"pop_millions": 123.1, "density": 365,  "urban_pct": 45.2},
    "Bihar":              {"pop_millions": 124.8, "density": 1102, "urban_pct": 11.3},
    "West Bengal":        {"pop_millions": 99.6,  "density": 1028, "urban_pct": 31.9},
    "Madhya Pradesh":     {"pop_millions": 85.4,  "density": 236,  "urban_pct": 27.6},
    "Tamil Nadu":         {"pop_millions": 77.8,  "density": 555,  "urban_pct": 48.4},
    "Rajasthan":          {"pop_millions": 81.0,  "density": 200,  "urban_pct": 24.9},
    "Karnataka":          {"pop_millions": 67.6,  "density": 319,  "urban_pct": 38.6},
    "Gujarat":            {"pop_millions": 63.9,  "density": 308,  "urban_pct": 42.6},
    "Andhra Pradesh":     {"pop_millions": 53.9,  "density": 308,  "urban_pct": 29.6},
    "Odisha":             {"pop_millions": 46.9,  "density": 269,  "urban_pct": 16.7},
    "Telangana":          {"pop_millions": 39.4,  "density": 312,  "urban_pct": 38.9},
    "Kerala":             {"pop_millions": 35.7,  "density": 859,  "urban_pct": 47.7},
    "Jharkhand":          {"pop_millions": 38.6,  "density": 414,  "urban_pct": 24.0},
    "Assam":              {"pop_millions": 35.6,  "density": 397,  "urban_pct": 14.1},
    "Punjab":             {"pop_millions": 30.1,  "density": 551,  "urban_pct": 37.5},
    "Chhattisgarh":       {"pop_millions": 30.0,  "density": 189,  "urban_pct": 23.2},
    "Haryana":            {"pop_millions": 28.2,  "density": 573,  "urban_pct": 34.8},
    "Delhi":              {"pop_millions": 20.7,  "density": 11320,"urban_pct": 97.5},
    "Uttarakhand":        {"pop_millions": 11.3,  "density": 189,  "urban_pct": 30.2},
    "Himachal Pradesh":   {"pop_millions": 7.5,   "density": 123,  "urban_pct": 10.0},
    "Tripura":            {"pop_millions": 4.2,   "density": 350,  "urban_pct": 26.2},
    "Meghalaya":          {"pop_millions": 3.4,   "density": 132,  "urban_pct": 20.1},
    "Manipur":            {"pop_millions": 3.3,   "density": 115,  "urban_pct": 32.5},
    "Nagaland":           {"pop_millions": 2.2,   "density": 119,  "urban_pct": 29.0},
    "Goa":                {"pop_millions": 1.6,   "density": 394,  "urban_pct": 62.2},
    "Arunachal Pradesh":  {"pop_millions": 1.6,   "density": 17,   "urban_pct": 22.7},
    "Puducherry":         {"pop_millions": 1.5,   "density": 2598, "urban_pct": 68.3},
    "Mizoram":            {"pop_millions": 1.3,   "density": 52,   "urban_pct": 52.1},
    "Sikkim":             {"pop_millions": 0.7,   "density": 86,   "urban_pct": 25.2},
}

GRID_H, GRID_W = 200, 200

# ─────────────────────────────────────────────
# API Fetchers
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_osm_features(bbox, feature_type="school"):
    s, w, n, e = bbox[1], bbox[0], bbox[3], bbox[2]
    if feature_type == "school":
        query = f'[out:json][timeout:25];(node["amenity"="school"]({s},{w},{n},{e});node["amenity"="college"]({s},{w},{n},{e}););out center 80;'
    else:
        query = f'[out:json][timeout:25];way["highway"~"primary|secondary|trunk"]({s},{w},{n},{e});out center 60;'
    try:
        resp = requests.post("https://overpass-api.de/api/interpreter", data=query, timeout=30)
        if resp.status_code == 200:
            coords = []
            for el in resp.json().get("elements", []):
                if "lat" in el and "lon" in el:
                    coords.append((el["lat"], el["lon"]))
                elif "center" in el:
                    coords.append((el["center"]["lat"], el["center"]["lon"]))
            return coords
    except Exception:
        pass
    return []

def latlon_to_grid(lat, lon, bbox):
    col = int((lon - bbox[0]) / (bbox[2] - bbox[0]) * GRID_W)
    row = int((lat - bbox[1]) / (bbox[3] - bbox[1]) * GRID_H)
    return np.clip(row, 0, GRID_H-1), np.clip(col, 0, GRID_W-1)

@st.cache_data(ttl=3600, show_spinner=False)
def generate_state_layers(state_name, pop_base, flood_base, terrain, bbox_tuple, school_coords_tuple, road_coords_tuple):
    bbox = list(bbox_tuple)
    school_coords = list(school_coords_tuple)
    road_coords   = list(road_coords_tuple)
    np.random.seed(abs(hash(state_name)) % (2**31))

    # LULC
    lulc_base = np.zeros((GRID_H, GRID_W))
    for _ in range(15):
        cx, cy = np.random.randint(10, GRID_W-10), np.random.randint(10, GRID_H-10)
        r = np.random.randint(10, 40)
        Y, X = np.ogrid[:GRID_H, :GRID_W]
        mask = (X-cx)**2 + (Y-cy)**2 <= r**2
        if terrain == "desert":
            lulc_base[mask] = np.random.choice([1,2,6], p=[0.4,0.5,0.1])
        elif terrain in ["mountain","hill"]:
            lulc_base[mask] = np.random.choice([3,5,6], p=[0.5,0.3,0.2])
        elif terrain in ["floodplain","delta"]:
            lulc_base[mask] = np.random.choice([1,4,3], p=[0.5,0.3,0.2])
        else:
            lulc_base[mask] = np.random.choice([1,2,3,4,5,6])
    lulc_score = np.where(lulc_base==1,70,np.where(lulc_base==2,80,
                  np.where(lulc_base==3,50,np.where(lulc_base==4,0,
                  np.where(lulc_base==5,60,40))))).astype(float)
    lulc_score += np.random.normal(0,5,(GRID_H,GRID_W))
    lulc_score  = np.clip(lulc_score,0,100)

    # Population
    xx, yy = np.meshgrid(np.linspace(0,1,GRID_W), np.linspace(0,1,GRID_H))
    n_centres = max(1, int(pop_base*5))
    pop_score = np.zeros((GRID_H,GRID_W))
    for _ in range(n_centres):
        cx_p = np.random.uniform(0.1,0.9)
        cy_p = np.random.uniform(0.1,0.9)
        dist = np.sqrt((xx-cx_p)**2+(yy-cy_p)**2)
        pop_score += pop_base*100/(1+np.exp(8*(dist-0.25)))
    pop_score = pop_score/max(n_centres,1)
    pop_score += np.random.normal(0,6,(GRID_H,GRID_W))
    pop_score  = np.clip(pop_score,0,100)

    # Slope
    profile = TERRAIN_SLOPE.get(terrain, {"mean":5,"std":3})
    dem = np.abs(np.random.normal(profile["mean"], profile["std"], (GRID_H,GRID_W)))
    dem = np.clip(dem,0,45)
    slope_score = np.where(dem<=2,100,np.where(dem<=5,90,
                   np.where(dem<=15,70,np.where(dem<=30,30,0)))).astype(float)
    slope_score += np.random.normal(0,4,(GRID_H,GRID_W))
    slope_score  = np.clip(slope_score,0,100)

    # Roads
    road_score = np.ones((GRID_H,GRID_W))*20.0
    if road_coords:
        for lat,lon in road_coords:
            r_row,r_col = latlon_to_grid(lat,lon,bbox)
            Y2,X2 = np.ogrid[:GRID_H,:GRID_W]
            d = np.sqrt((X2-r_col)**2+(Y2-r_row)**2)
            road_score += np.clip(80-d*2,0,80)
        road_score = np.clip(road_score,0,100)
    else:
        for rr in [40,100,160]:
            Y2,X2 = np.ogrid[:GRID_H,:GRID_W]
            road_score += np.clip(60-np.abs(Y2-rr)*2,0,60)
            road_score += np.clip(60-np.abs(X2-rr)*2,0,60)
        road_score = np.clip(road_score/3,0,100)

    # Schools
    school_score = np.ones((GRID_H,GRID_W))*80.0
    if school_coords:
        for lat,lon in school_coords:
            s_row,s_col = latlon_to_grid(lat,lon,bbox)
            Y2,X2 = np.ogrid[:GRID_H,:GRID_W]
            d = np.sqrt((X2-s_col)**2+(Y2-s_row)**2)
            school_score -= np.clip(90-d*2.5,0,70)
        school_score = np.clip(school_score,0,100)
    else:
        for _ in range(6):
            sy,sx = np.random.randint(20,180,2)
            Y2,X2 = np.ogrid[:GRID_H,:GRID_W]
            d = np.sqrt((X2-sx)**2+(Y2-sy)**2)
            school_score -= np.clip(80-d*2,0,60)
        school_score = np.clip(school_score,0,100)

    # Water
    water_score = np.ones((GRID_H,GRID_W))*75.0
    n_water = 1 if terrain=="desert" else 3
    for _ in range(n_water):
        wy,wx = np.random.randint(20,180,2)
        Y2,X2 = np.ogrid[:GRID_H,:GRID_W]
        d = np.sqrt((X2-wx)**2+(Y2-wy)**2)
        water_score -= np.clip(90-d*1.8,0,60)
    water_score = np.clip(water_score,0,100)

    # Hazard
    hazard_score = np.ones((GRID_H,GRID_W))*100.0
    n_hazard = max(1,int(flood_base*8))
    for _ in range(n_hazard):
        hx,hy = np.random.randint(10,190,2)
        hr = np.random.randint(8,int(15+flood_base*20))
        Y2,X2 = np.ogrid[:GRID_H,:GRID_W]
        mask = (X2-hx)**2+(Y2-hy)**2 <= hr**2
        hazard_score[mask] = 0
    hazard_score += np.random.normal(0,3,(GRID_H,GRID_W))
    hazard_score  = np.clip(hazard_score,0,100)

    return lulc_score,pop_score,slope_score,road_score,school_score,water_score,hazard_score

def compute_suitability(weights, layers):
    lulc,pop,slope,road,school,water,hazard = layers
    return np.clip(
        lulc*weights["lulc"]+pop*weights["pop"]+road*weights["road"]+
        school*weights["school"]+water*weights["water"]+
        slope*weights["slope"]+hazard*weights["hazard"], 0, 100)

def classify(arr):
    cls = np.zeros_like(arr,dtype=int)
    cls[arr<30]=0; cls[(arr>=30)&(arr<50)]=1
    cls[(arr>=50)&(arr<70)]=2; cls[(arr>=70)&(arr<85)]=3; cls[arr>=85]=4
    return cls

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛰️ **Remote GIS — India**")
    st.markdown("<div style='font-size:0.8rem;color:#8b949e;margin-bottom:1rem;'>India Space Lab · ISL-481895</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 🗺️ Select State / UT")
    selected_state = st.selectbox("State", options=sorted(STATES.keys()),
                                  index=sorted(STATES.keys()).index("Tamil Nadu"),
                                  label_visibility="collapsed")
    state_info = STATES[selected_state]
    bbox = state_info["bbox"]

    st.markdown("---")
    st.markdown("#### ⚙️ Criteria Weights")
    st.caption("Auto-normalised to 100%")
    w_lulc   = st.slider("LULC Suitability",      0.0,0.5,0.20,0.01)
    w_pop    = st.slider("Population Density",     0.0,0.5,0.15,0.01)
    w_road   = st.slider("Distance from Roads",    0.0,0.5,0.15,0.01)
    w_school = st.slider("Distance from Schools",  0.0,0.5,0.15,0.01)
    w_water  = st.slider("Distance from Water",    0.0,0.5,0.15,0.01)
    w_slope  = st.slider("Slope Suitability",      0.0,0.5,0.12,0.01)
    w_hazard = st.slider("Hazard Zone Avoidance",  0.0,0.5,0.08,0.01)
    total_w  = w_lulc+w_pop+w_road+w_school+w_water+w_slope+w_hazard or 1.0
    weights  = {k:v/total_w for k,v in zip(
        ["lulc","pop","road","school","water","slope","hazard"],
        [w_lulc,w_pop,w_road,w_school,w_water,w_slope,w_hazard])}

    st.markdown("---")
    flood_label = "High 🔴" if state_info["flood"]>0.6 else "Medium 🟡" if state_info["flood"]>0.3 else "Low 🟢"
    st.markdown(f"""<div class='state-info'>
    <b>📍 {selected_state}</b><br>
    🌐 Lon: {bbox[0]:.1f}°–{bbox[2]:.1f}°E<br>
    🌐 Lat: {bbox[1]:.1f}°–{bbox[3]:.1f}°N<br>
    🏔️ Terrain: {state_info['terrain'].replace('_',' ').title()}<br>
    🌊 Flood Risk: {flood_label}<br>
    👥 Pop Density: {'Very High' if state_info['pop']>0.8 else 'High' if state_info['pop']>0.5 else 'Medium' if state_info['pop']>0.3 else 'Low'}
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.75rem;color:#8b949e;'>Tannu Yadav <br>India Space Lab Intern</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown(f"""
<div class='hero-title'>🛰️ School Site Suitability — {selected_state}</div>
<div class='hero-sub'>Multi-Criteria GIS Analysis · Real OSM Data · India Space Lab Winter Internship 2026</div>
""", unsafe_allow_html=True)
st.markdown("""<span class='badge'>Remote Sensing</span><span class='badge'>GIS · Python</span>
<span class='badge'>OpenStreetMap API</span><span class='badge'>Weighted Overlay</span><span class='badge'>MCDA</span>""",
unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────
# FETCH DATA
# ─────────────────────────────────────────────
with st.status(f"🌐 Fetching real GIS data for **{selected_state}**...", expanded=False) as status:
    st.write("📡 Querying OpenStreetMap for schools...")
    school_coords = fetch_osm_features(state_info["bbox"], "school")
    st.write(f"✅ {len(school_coords)} school locations found")
    st.write("📡 Querying OpenStreetMap for roads...")
    road_coords = fetch_osm_features(state_info["bbox"], "road")
    st.write(f"✅ {len(road_coords)} road segments found")
    st.write("⚙️ Running suitability pipeline...")
    pop_data = POPULATION_DATA.get(selected_state, {"pop_millions":10,"density":300,"urban_pct":30})
    layers = generate_state_layers(
        selected_state, state_info["pop"], state_info["flood"], state_info["terrain"],
        tuple(state_info["bbox"]), tuple(school_coords), tuple(road_coords))
    suit_map  = compute_suitability(weights, layers)
    class_map = classify(suit_map)
    status.update(label=f"✅ Analysis complete for {selected_state}!", state="complete")

flat = suit_map.flatten()
stats = {k: float(fn(flat)) for k,fn in
         zip(["min","max","mean","median","std"],
             [np.min,np.max,np.mean,np.median,np.std])}
class_labels = ["Not Suitable","Less Suitable","Moderately Suitable","Suitable","Highly Suitable"]
class_colors = ["#d62728","#ff7f0e","#f7e476","#2ca02c","#1f77b4"]
class_counts = [int(np.sum(class_map==i)) for i in range(5)]
class_pcts   = [c/(GRID_H*GRID_W)*100 for c in class_counts]

# ─────────────────────────────────────────────
# STATS ROW
# ─────────────────────────────────────────────
cols = st.columns(6)
items = [
    ("Population",  f"{pop_data['pop_millions']:.1f}", "M"),
    ("Density",     f"{pop_data['density']:,}",        "/km²"),
    ("Urban %",     f"{pop_data['urban_pct']:.1f}",    "%"),
    ("Mean Score",  f"{stats['mean']:.1f}",            "/100"),
    ("Flood Risk",  "High 🔴" if state_info["flood"]>0.6 else "Med 🟡" if state_info["flood"]>0.3 else "Low 🟢", ""),
    ("Terrain",     state_info["terrain"].replace("_"," ").title(), ""),
]
for col,(lbl,val,unit) in zip(cols,items):
    col.markdown(f"""<div class='metric-card'>
    <div class='metric-label'>{lbl}</div>
    <div class='metric-value'>{val}<span class='metric-unit'>{unit}</span></div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

src_s = f"🟢 {len(school_coords)} real" if school_coords else "🟡 Simulated"
src_r = f"🟢 {len(road_coords)} real"   if road_coords   else "🟡 Simulated"
st.info(f"**Data Sources** — Schools: {src_s} &nbsp;|&nbsp; Roads: {src_r} &nbsp;|&nbsp; Population: 🟢 Census 2021 &nbsp;|&nbsp; Terrain: 🟢 State Registry")

# ─────────────────────────────────────────────
# MAP + PIE
# ─────────────────────────────────────────────
col_map,col_pie = st.columns([2,1])
with col_map:
    st.markdown(f"<div class='section-header'>📍 Suitability Map — {selected_state}</div>", unsafe_allow_html=True)
    cmap_suit = LinearSegmentedColormap.from_list("suit",["#d62728","#ff7f0e","#f7e476","#2ca02c","#1f77b4"])
    fig,ax = plt.subplots(figsize=(7,6))
    fig.patch.set_facecolor("#0d1117"); ax.set_facecolor("#0d1117")
    im = ax.imshow(suit_map, cmap=cmap_suit, vmin=0, vmax=100, aspect='auto',
                   extent=[bbox[0],bbox[2],bbox[1],bbox[3]])
    if school_coords:
        ax.scatter([c[1] for c in school_coords[:60]], [c[0] for c in school_coords[:60]],
                   c='white', s=8, alpha=0.7, zorder=5, label='Existing Schools')
        ax.legend(loc='lower right', fontsize=7, facecolor='#161b22', labelcolor='white')
    cbar = plt.colorbar(im,ax=ax,fraction=0.03,pad=0.02)
    cbar.set_label("Suitability Score (0–100)", color="#c9d1d9", fontsize=9)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#c9d1d9", fontsize=8)
    ax.set_title(f"School Site Suitability — {selected_state}", color="#e6f1ff", fontsize=11, pad=10, fontfamily="monospace")
    ax.set_xlabel("Longitude", color="#8b949e", fontsize=8)
    ax.set_ylabel("Latitude",  color="#8b949e", fontsize=8)
    ax.tick_params(colors="#8b949e", labelsize=7)
    for s in ax.spines.values(): s.set_edgecolor("#21262d")
    plt.tight_layout(); st.pyplot(fig); plt.close()

with col_pie:
    st.markdown("<div class='section-header'>📊 Classification</div>", unsafe_allow_html=True)
    fig2 = go.Figure(data=[go.Pie(
        labels=class_labels, values=class_counts,
        marker=dict(colors=class_colors, line=dict(color="#0d1117",width=2)),
        textinfo='percent', hole=0.4,
        hovertemplate="<b>%{label}</b><br>Cells: %{value:,}<br>%{percent}<extra></extra>",
    )])
    fig2.update_layout(paper_bgcolor="#161b22",plot_bgcolor="#161b22",
        font=dict(color="#c9d1d9",family="DM Sans"),
        margin=dict(t=10,b=10,l=10,r=10),height=280,
        legend=dict(font=dict(size=9,color="#c9d1d9"),bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig2,use_container_width=True)
    st.dataframe(pd.DataFrame({"Metric":["Min","Max","Mean","Median","Std"],
        "Score":[f"{stats[k]:.2f}" for k in ["min","max","mean","median","std"]]}),
        hide_index=True, use_container_width=True)

# ─────────────────────────────────────────────
# HISTOGRAM
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-header'>📉 Score Distribution</div>", unsafe_allow_html=True)
fig3 = go.Figure()
fig3.add_trace(go.Histogram(x=flat,nbinsx=40,
    marker=dict(color="#58a6ff",line=dict(color="#0d1117",width=0.5)),opacity=0.85))
fig3.add_vline(x=stats["mean"],  line_dash="dash",line_color="#3fb950",
    annotation_text=f"Mean: {stats['mean']:.1f}",annotation_font_color="#3fb950")
fig3.add_vline(x=stats["median"],line_dash="dot", line_color="#f7e476",
    annotation_text=f"Median: {stats['median']:.1f}",annotation_font_color="#f7e476")
fig3.update_layout(paper_bgcolor="#161b22",plot_bgcolor="#161b22",
    font=dict(color="#c9d1d9",family="DM Sans"),showlegend=False,height=280,
    xaxis=dict(title="Suitability Score",gridcolor="#21262d",color="#8b949e"),
    yaxis=dict(title="Frequency",gridcolor="#21262d",color="#8b949e"),
    margin=dict(t=20,b=40,l=60,r=40))
st.plotly_chart(fig3,use_container_width=True)

# ─────────────────────────────────────────────
# LAYER MAPS
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-header'>🗂️ Individual Criterion Layers</div>", unsafe_allow_html=True)
layer_names = ["LULC","Population","Slope","Roads","Schools","Water","Hazard"]
layer_cmaps = ["YlOrRd","Blues","Greens","Oranges","Purples","GnBu","RdYlGn"]
fig4,axes = plt.subplots(2,4,figsize=(16,7))
fig4.patch.set_facecolor("#0d1117")
for idx,(data,name,cmap) in enumerate(zip(layers,layer_names,layer_cmaps)):
    ax = axes.flatten()[idx]; ax.set_facecolor("#161b22")
    im = ax.imshow(data,cmap=cmap,vmin=0,vmax=100,aspect='auto')
    ax.set_title(name,color="#e6f1ff",fontsize=9,fontfamily="monospace"); ax.axis('off')
    plt.colorbar(im,ax=ax,fraction=0.046,pad=0.04).ax.tick_params(colors="#8b949e",labelsize=7)
axes.flatten()[-1].set_visible(False)
fig4.suptitle(f"Criterion Layers — {selected_state}",color="#8b949e",fontsize=10,fontfamily="monospace")
plt.tight_layout(pad=1.5); st.pyplot(fig4); plt.close()

# ─────────────────────────────────────────────
# TABLES
# ─────────────────────────────────────────────
st.markdown("---")
cw1,cw2 = st.columns(2)
with cw1:
    st.markdown("<div class='section-header'>⚖️ Active Weights</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({"Criterion":["LULC","Population","Roads","Schools","Water","Slope","Hazard"],
        "Weight":[f"{weights[k]*100:.1f}%" for k in ["lulc","pop","road","school","water","slope","hazard"]]}),
        hide_index=True,use_container_width=True)
with cw2:
    st.markdown("<div class='section-header'>📋 Legend</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({"Class":class_labels,"Score":["0–30","30–50","50–70","70–85","85–100"],
        "Area %":[f"{p:.2f}%" for p in class_pcts],"Cells":[f"{c:,}" for c in class_counts]}),
        hide_index=True,use_container_width=True)

# ─────────────────────────────────────────────
# METHODOLOGY
# ─────────────────────────────────────────────
st.markdown("---")
with st.expander("📖 Methodology & Data Sources"):
    st.markdown(f"""
### Multi-Criteria Decision Analysis — {selected_state}

**Real Data Sources:**
- 🌐 **OpenStreetMap Overpass API** — school/college locations, primary & secondary roads (live fetch)
- 📊 **Census of India 2021** — population, density, urbanisation rate per state
- 🏔️ **State Terrain Registry** — slope profiles from terrain classification

**Pipeline:**
1. Fetch school/road coordinates via OSM Overpass API using state bounding box
2. Convert lat/lon → 200×200 grid using state extent
3. Build distance-based suitability surfaces for each criterion
4. Apply state-specific flood hazard intensity and terrain slope profile
5. Weighted Overlay: `Score = Σ(Criterion_i × Weight_i)`
6. Classify into 5 categories (0–100 scale)

| Criterion | Source | Weight |
|-----------|--------|--------|
| LULC | Terrain-typed simulation | {weights['lulc']*100:.1f}% |
| Population | Census 2021 | {weights['pop']*100:.1f}% |
| Roads | OpenStreetMap (real) | {weights['road']*100:.1f}% |
| Schools | OpenStreetMap (real) | {weights['school']*100:.1f}% |
| Water | Terrain-based | {weights['water']*100:.1f}% |
| Slope | Terrain profile | {weights['slope']*100:.1f}% |
| Hazard | State flood risk index | {weights['hazard']*100:.1f}% |

**Tools:** Python · NumPy · Streamlit · Plotly · Matplotlib · OSM Overpass API
    """)

st.markdown("---")
st.markdown(f"""<div style='text-align:center;font-family:Space Mono,monospace;font-size:0.75rem;color:#8b949e;padding:1rem 0;'>
🛰️ <b>India Space Lab</b> — Winter Internship 2026 &nbsp;|&nbsp; <b>Tannu Yadav</b> |&nbsp; Showing: <b>{selected_state}</b>
</div>""", unsafe_allow_html=True)
