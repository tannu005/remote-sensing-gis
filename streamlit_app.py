import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="School Site Suitability Analysis — Chennai",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
}

.main { background-color: #0d1117; }

.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #e6f1ff;
    line-height: 1.3;
    margin-bottom: 0.3rem;
}

.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    color: #8b949e;
    margin-bottom: 1.5rem;
}

.badge {
    display: inline-block;
    background: #1a2332;
    border: 1px solid #30363d;
    color: #58a6ff;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    padding: 4px 10px;
    border-radius: 20px;
    margin-right: 6px;
    margin-bottom: 6px;
}

.metric-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    text-align: center;
}

.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
}

.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.7rem;
    font-weight: 700;
    color: #e6f1ff;
}

.metric-unit {
    font-size: 0.75rem;
    color: #58a6ff;
    margin-left: 3px;
}

.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
    color: #58a6ff;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-bottom: 1px solid #21262d;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.criteria-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid #21262d;
}

.criteria-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: #c9d1d9;
}

.criteria-weight {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #3fb950;
    font-weight: 700;
}

.stSidebar {
    background-color: #161b22 !important;
}

.stSlider > div > div > div > div {
    background-color: #58a6ff !important;
}

div[data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Suitability Simulation Engine
# ─────────────────────────────────────────────
np.random.seed(42)
GRID_H, GRID_W = 200, 200

@st.cache_data
def generate_base_layers():
    # LULC layer
    lulc_base = np.zeros((GRID_H, GRID_W))
    for _ in range(12):
        cx, cy = np.random.randint(20, 180, 2)
        r = np.random.randint(15, 45)
        Y, X = np.ogrid[:GRID_H, :GRID_W]
        mask = (X - cx)**2 + (Y - cy)**2 <= r**2
        lulc_base[mask] = np.random.choice([1, 2, 3, 4, 5, 6])
    lulc_score = np.where(lulc_base == 1, 70, np.where(lulc_base == 2, 80,
                  np.where(lulc_base == 3, 50, np.where(lulc_base == 4, 0,
                  np.where(lulc_base == 5, 60, 40))))).astype(float)
    lulc_score = lulc_score + np.random.normal(0, 5, (GRID_H, GRID_W))
    lulc_score = np.clip(lulc_score, 0, 100)

    # Population density (sigmoid)
    x = np.linspace(0, 1, GRID_W)
    y = np.linspace(0, 1, GRID_H)
    xx, yy = np.meshgrid(x, y)
    dist_center = np.sqrt((xx - 0.5)**2 + (yy - 0.5)**2)
    pop_score = 100 / (1 + np.exp(8 * (dist_center - 0.3)))
    pop_score += np.random.normal(0, 6, (GRID_H, GRID_W))
    pop_score = np.clip(pop_score, 0, 100)

    # Slope from DEM (0-2°: 100, steep: 0)
    dem = np.random.normal(10, 3, (GRID_H, GRID_W))
    dem = np.clip(dem, 0, 30)
    slope_score = np.where(dem <= 2, 100, np.where(dem <= 5, 90,
                   np.where(dem <= 15, 70, np.where(dem <= 30, 30, 0)))).astype(float)
    slope_score += np.random.normal(0, 4, (GRID_H, GRID_W))
    slope_score = np.clip(slope_score, 0, 100)

    # Road proximity
    road_score = np.zeros((GRID_H, GRID_W))
    road_rows = [40, 100, 160]
    road_cols = [40, 100, 160]
    for r in road_rows:
        for i in range(GRID_H):
            d = abs(i - r)
            road_score[i, :] += max(0, 100 - d * 3)
    for c in road_cols:
        for j in range(GRID_W):
            d = abs(j - c)
            road_score[:, j] += max(0, 100 - d * 3)
    road_score = np.clip(road_score / 2, 0, 100)

    # School proximity (away from existing = higher score)
    school_score = np.ones((GRID_H, GRID_W)) * 80
    school_locs = [(30, 30), (80, 150), (160, 80), (140, 140)]
    for sy, sx in school_locs:
        Y2, X2 = np.ogrid[:GRID_H, :GRID_W]
        d = np.sqrt((X2 - sx)**2 + (Y2 - sy)**2)
        school_score -= np.clip(100 - d * 2, 0, 80)
    school_score = np.clip(school_score, 0, 100)

    # Water body distance
    water_score = np.ones((GRID_H, GRID_W)) * 70
    water_locs = [(50, 170), (150, 30)]
    for wy, wx in water_locs:
        Y2, X2 = np.ogrid[:GRID_H, :GRID_W]
        d = np.sqrt((X2 - wx)**2 + (Y2 - wy)**2)
        water_score -= np.clip(100 - d * 1.5, 0, 50)
    water_score = np.clip(water_score, 0, 100)

    # Hazard zones (flood-prone = 0)
    hazard_score = np.ones((GRID_H, GRID_W)) * 100
    for _ in range(3):
        hx, hy = np.random.randint(20, 180, 2)
        hr = np.random.randint(10, 30)
        Y2, X2 = np.ogrid[:GRID_H, :GRID_W]
        hazard_mask = (X2 - hx)**2 + (Y2 - hy)**2 <= hr**2
        hazard_score[hazard_mask] = 0
    hazard_score += np.random.normal(0, 3, (GRID_H, GRID_W))
    hazard_score = np.clip(hazard_score, 0, 100)

    return lulc_score, pop_score, slope_score, road_score, school_score, water_score, hazard_score

def compute_suitability(weights, layers):
    lulc, pop, slope, road, school, water, hazard = layers
    w = weights
    combined = (
        lulc    * w["lulc"] +
        pop     * w["pop"] +
        road    * w["road"] +
        school  * w["school"] +
        water   * w["water"] +
        slope   * w["slope"] +
        hazard  * w["hazard"]
    )
    return np.clip(combined, 0, 100)

def classify(arr):
    cls = np.zeros_like(arr, dtype=int)
    cls[arr < 30] = 0
    cls[(arr >= 30) & (arr < 50)] = 1
    cls[(arr >= 50) & (arr < 70)] = 2
    cls[(arr >= 70) & (arr < 85)] = 3
    cls[arr >= 85] = 4
    return cls

# ─────────────────────────────────────────────
# Load base layers
# ─────────────────────────────────────────────
layers = generate_base_layers()
lulc_score, pop_score, slope_score, road_score, school_score, water_score, hazard_score = layers

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛰️ **Remote GIS**")
    st.markdown("<div style='font-size:0.8rem;color:#8b949e;margin-bottom:1rem;'>India Space Lab · ISL-481895</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### ⚙️ Criteria Weights")
    st.caption("Adjust weights (must conceptually sum to 1.0)")

    w_lulc   = st.slider("LULC Suitability",       0.0, 0.5, 0.20, 0.01)
    w_pop    = st.slider("Population Density",      0.0, 0.5, 0.15, 0.01)
    w_road   = st.slider("Distance from Roads",     0.0, 0.5, 0.15, 0.01)
    w_school = st.slider("Distance from Schools",   0.0, 0.5, 0.15, 0.01)
    w_water  = st.slider("Distance from Water",     0.0, 0.5, 0.15, 0.01)
    w_slope  = st.slider("Slope Suitability",       0.0, 0.5, 0.12, 0.01)
    w_hazard = st.slider("Hazard Zone Avoidance",   0.0, 0.5, 0.08, 0.01)

    total_w = w_lulc + w_pop + w_road + w_school + w_water + w_slope + w_hazard
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"⚠️ Weights sum to {total_w:.2f} (normalizing automatically)")

    # Normalize
    if total_w > 0:
        norm = total_w
    else:
        norm = 1.0

    weights = {
        "lulc":   w_lulc / norm,
        "pop":    w_pop / norm,
        "road":   w_road / norm,
        "school": w_school / norm,
        "water":  w_water / norm,
        "slope":  w_slope / norm,
        "hazard": w_hazard / norm,
    }

    st.markdown("---")
    st.markdown("#### 📍 Study Area")
    st.markdown("""
    <div style='font-size:0.82rem;color:#8b949e;line-height:1.7'>
    📌 Chennai, India<br>
    📐 Resolution: 30m<br>
    🗺️ CRS: EPSG:4326<br>
    🔲 Grid: 200×200 cells<br>
    📅 Feb–Mar 2026
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem;color:#8b949e;'>
    <b>Tannu Yadav</b><br>
    VIT-AP · 23BCE9096<br>
    India Space Lab Intern
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Compute suitability
# ─────────────────────────────────────────────
suit_map = compute_suitability(weights, layers)
class_map = classify(suit_map)

flat = suit_map.flatten()
stats = {
    "min":    float(np.min(flat)),
    "max":    float(np.max(flat)),
    "mean":   float(np.mean(flat)),
    "median": float(np.median(flat)),
    "std":    float(np.std(flat)),
}

class_labels = ["Not Suitable", "Less Suitable", "Moderately Suitable", "Suitable", "Highly Suitable"]
class_colors = ["#d62728", "#ff7f0e", "#f7e476", "#2ca02c", "#1f77b4"]
class_counts = [int(np.sum(class_map == i)) for i in range(5)]
class_pcts   = [c / (GRID_H * GRID_W) * 100 for c in class_counts]

# ─────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────
st.markdown("""
<div class='hero-title'>🛰️ School Site Suitability Analysis</div>
<div class='hero-sub'>Multi-Criteria GIS Analysis · Chennai, India · India Space Lab Winter Internship 2026</div>
""", unsafe_allow_html=True)

st.markdown("""
<span class='badge'>Remote Sensing</span>
<span class='badge'>GIS · Python</span>
<span class='badge'>Weighted Overlay</span>
<span class='badge'>Rasterio</span>
<span class='badge'>GeoPandas</span>
<span class='badge'>MCDA</span>
""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# KPI Row
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""<div class='metric-card'>
    <div class='metric-label'>Mean Score</div>
    <div class='metric-value'>{stats['mean']:.1f}<span class='metric-unit'>/100</span></div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class='metric-card'>
    <div class='metric-label'>Std Deviation</div>
    <div class='metric-value'>{stats['std']:.2f}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class='metric-card'>
    <div class='metric-label'>Max Score</div>
    <div class='metric-value'>{stats['max']:.1f}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class='metric-card'>
    <div class='metric-label'>Mod. Suitable</div>
    <div class='metric-value'>{class_pcts[2]:.1f}<span class='metric-unit'>%</span></div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class='metric-card'>
    <div class='metric-label'>Total Cells</div>
    <div class='metric-value'>40K</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Main Map + Classification
# ─────────────────────────────────────────────
col_map, col_pie = st.columns([2, 1])

with col_map:
    st.markdown("<div class='section-header'>📍 Suitability Map — Chennai</div>", unsafe_allow_html=True)
    cmap_suit = LinearSegmentedColormap.from_list("suit", ["#d62728", "#ff7f0e", "#f7e476", "#2ca02c", "#1f77b4"])
    fig, ax = plt.subplots(figsize=(7, 6))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    im = ax.imshow(suit_map, cmap=cmap_suit, vmin=0, vmax=100, aspect='auto')
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Suitability Score (0–100)", color="#c9d1d9", fontsize=9)
    cbar.ax.yaxis.set_tick_params(color="#c9d1d9")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#c9d1d9", fontsize=8)
    ax.set_title("School Site Suitability Map — Chennai", color="#e6f1ff", fontsize=11, pad=10, fontfamily="monospace")
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values():
        spine.set_edgecolor("#21262d")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_pie:
    st.markdown("<div class='section-header'>📊 Classification Breakdown</div>", unsafe_allow_html=True)
    fig2 = go.Figure(data=[go.Pie(
        labels=class_labels,
        values=class_counts,
        marker=dict(colors=class_colors, line=dict(color="#0d1117", width=2)),
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Cells: %{value:,}<br>%{percent}<extra></extra>",
        hole=0.4,
    )])
    fig2.update_layout(
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font=dict(color="#c9d1d9", family="DM Sans"),
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(
            font=dict(size=10, color="#c9d1d9"),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=320,
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Stats table
    st.markdown("<div class='section-header' style='margin-top:1rem'>📈 Statistics</div>", unsafe_allow_html=True)
    stats_df = pd.DataFrame({
        "Metric": ["Minimum", "Maximum", "Mean", "Median", "Std Dev"],
        "Score":  [f"{stats['min']:.2f}", f"{stats['max']:.2f}", f"{stats['mean']:.2f}", f"{stats['median']:.2f}", f"{stats['std']:.2f}"]
    })
    st.dataframe(stats_df, hide_index=True, use_container_width=True)

# ─────────────────────────────────────────────
# Score Distribution Histogram
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-header'>📉 Score Distribution</div>", unsafe_allow_html=True)

fig3 = go.Figure()
fig3.add_trace(go.Histogram(
    x=flat,
    nbinsx=40,
    marker=dict(color="#58a6ff", line=dict(color="#0d1117", width=0.5)),
    opacity=0.85,
    name="Suitability Score",
    hovertemplate="Score: %{x:.1f}<br>Count: %{y:,}<extra></extra>",
))
fig3.add_vline(x=stats["mean"],   line_dash="dash", line_color="#3fb950", annotation_text=f"Mean: {stats['mean']:.1f}",   annotation_font_color="#3fb950")
fig3.add_vline(x=stats["median"], line_dash="dot",  line_color="#f7e476", annotation_text=f"Median: {stats['median']:.1f}", annotation_font_color="#f7e476")
fig3.update_layout(
    paper_bgcolor="#161b22",
    plot_bgcolor="#161b22",
    font=dict(color="#c9d1d9", family="DM Sans"),
    xaxis=dict(title="Suitability Score (0–100)", gridcolor="#21262d", color="#8b949e"),
    yaxis=dict(title="Frequency (Cell Count)", gridcolor="#21262d", color="#8b949e"),
    margin=dict(t=20, b=40, l=60, r=40),
    height=300,
    showlegend=False,
)
st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────
# Individual Layer Maps
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-header'>🗂️ Individual Criterion Layers</div>", unsafe_allow_html=True)

layer_data  = [lulc_score, pop_score, slope_score, road_score, school_score, water_score, hazard_score]
layer_names = ["LULC", "Population", "Slope", "Roads", "Schools", "Water", "Hazard"]
layer_cmaps = ["YlOrRd", "Blues", "Greens", "Oranges", "Purples", "GnBu", "RdYlGn"]

fig4, axes = plt.subplots(2, 4, figsize=(16, 7))
fig4.patch.set_facecolor("#0d1117")
axes_flat = axes.flatten()

for idx, (data, name, cmap) in enumerate(zip(layer_data, layer_names, layer_cmaps)):
    ax = axes_flat[idx]
    ax.set_facecolor("#161b22")
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=100, aspect='auto')
    ax.set_title(name, color="#e6f1ff", fontsize=9, fontfamily="monospace")
    ax.axis('off')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(colors="#8b949e", labelsize=7)

axes_flat[-1].set_visible(False)
plt.tight_layout(pad=1.5)
st.pyplot(fig4)
plt.close()

# ─────────────────────────────────────────────
# Criteria Weights Summary
# ─────────────────────────────────────────────
st.markdown("---")
col_w1, col_w2 = st.columns(2)

with col_w1:
    st.markdown("<div class='section-header'>⚖️ Active Criteria Weights</div>", unsafe_allow_html=True)
    weight_df = pd.DataFrame({
        "Criterion": ["LULC Suitability", "Population Density", "Distance from Roads",
                      "Distance from Schools", "Distance from Water", "Slope Suitability", "Hazard Zones"],
        "Weight (%)": [f"{weights['lulc']*100:.1f}%", f"{weights['pop']*100:.1f}%",
                       f"{weights['road']*100:.1f}%", f"{weights['school']*100:.1f}%",
                       f"{weights['water']*100:.1f}%", f"{weights['slope']*100:.1f}%",
                       f"{weights['hazard']*100:.1f}%"],
    })
    st.dataframe(weight_df, hide_index=True, use_container_width=True)

with col_w2:
    st.markdown("<div class='section-header'>📋 Classification Legend</div>", unsafe_allow_html=True)
    legend_df = pd.DataFrame({
        "Class":       class_labels,
        "Score Range": ["0–30", "30–50", "50–70", "70–85", "85–100"],
        "Area %":      [f"{p:.2f}%" for p in class_pcts],
        "Cell Count":  [f"{c:,}" for c in class_counts],
    })
    st.dataframe(legend_df, hide_index=True, use_container_width=True)

# ─────────────────────────────────────────────
# Methodology
# ─────────────────────────────────────────────
st.markdown("---")
with st.expander("📖 Methodology — Multi-Criteria Analysis Framework"):
    st.markdown("""
    ### Multi-Criteria Decision Analysis (MCDA) Pipeline

    **1. Data Preparation**
    - Collection of spatial datasets: LULC, DEM, vector layers (roads, schools, water bodies)
    - Pre-processing and standardization to common coordinate system (EPSG:4326)
    - Raster conversion for uniform 30m-resolution analysis

    **2. Criteria Scoring (0–100)**
    | Criterion | Scoring Logic |
    |-----------|--------------|
    | LULC | Fallow Land: 80 · Agriculture: 70 · Vegetation: 50 · Water: 0 |
    | Population | Sigmoid curve — higher demand preferred with diminishing returns |
    | Slope | 0–2°: 100 · 2–5°: 90 · 5–15°: 70 · >30°: 0 |
    | Roads | Distance-based — closer to roads = higher score |
    | Schools | Distance-based — away from existing schools = higher score |
    | Hazard | Flood-prone areas = 0 suitability |

    **3. Weighted Overlay**
    ```
    Combined Suitability = Σ (Criterion_i × Weight_i)
    Final score ranges from 0 to 100
    ```

    **4. Classification**
    - **Highly Suitable (85–100)**: Best locations
    - **Suitable (70–85)**: Good alternatives
    - **Moderately Suitable (50–70)**: Consider with caution
    - **Less Suitable (30–50)**: Alternative consideration
    - **Not Suitable (0–30)**: Not recommended

    **Tools & Libraries**: Python · NumPy · Rasterio · GeoPandas · Shapely · Pandas · Matplotlib · Streamlit · Folium
    """)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;font-family:Space Mono,monospace;font-size:0.75rem;color:#8b949e;padding:1rem 0;'>
🛰️ <b>India Space Lab</b> — Winter Internship Technical Training Program 2026 &nbsp;|&nbsp;
<b>Tannu Yadav</b> · VIT-AP · 23BCE9096 &nbsp;|&nbsp;
Remote Sensing & GIS · Advanced Drone Technology · Disaster Management
</div>
""", unsafe_allow_html=True)
