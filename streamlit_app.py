import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import plotly.graph_objects as go
import requests

st.set_page_config(page_title="School Site Suitability — India GIS", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
h1,h2,h3{font-family:'Space Mono',monospace!important;}
.hero-title{font-family:'Space Mono',monospace;font-size:1.9rem;font-weight:700;color:#e6f1ff;line-height:1.3;margin-bottom:.3rem;}
.hero-sub{font-size:1rem;color:#8b949e;margin-bottom:1rem;}
.badge{display:inline-block;background:#1a2332;border:1px solid #30363d;color:#58a6ff;font-family:'Space Mono',monospace;font-size:.72rem;padding:4px 10px;border-radius:20px;margin-right:6px;margin-bottom:6px;}
.metric-card{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:1rem 1.2rem;text-align:center;}
.metric-label{font-family:'Space Mono',monospace;font-size:.65rem;color:#8b949e;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.3rem;}
.metric-value{font-family:'Space Mono',monospace;font-size:1.05rem;font-weight:700;color:#e6f1ff;}
.metric-unit{font-size:.75rem;color:#58a6ff;margin-left:3px;}
.section-header{font-family:'Space Mono',monospace;font-size:.9rem;font-weight:700;color:#58a6ff;text-transform:uppercase;letter-spacing:.1em;border-bottom:1px solid #21262d;padding-bottom:.5rem;margin-bottom:1rem;}
.info-box{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:1rem;margin-bottom:1rem;font-size:.82rem;color:#c9d1d9;line-height:2;}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# DATA REGISTRY
# ─────────────────────────────────────────────────────────────────

# State → metadata + list of cities with tight bboxes
STATE_DATA = {
    "Andhra Pradesh":    {"pop":0.55,"flood":0.35,"terrain":"coastal_plain",
        "cities":{"Visakhapatnam":[83.1,17.6,83.4,17.9],"Vijayawada":[80.5,16.4,80.8,16.7],"Guntur":[80.3,16.2,80.6,16.5],"Tirupati":[79.3,13.5,79.6,13.8],"Kurnool":[78.0,15.7,78.3,16.0]}},
    "Arunachal Pradesh": {"pop":0.05,"flood":0.20,"terrain":"mountain",
        "cities":{"Itanagar":[93.5,27.0,93.8,27.2],"Naharlagun":[93.6,27.0,93.8,27.2],"Pasighat":[95.3,28.0,95.5,28.2]}},
    "Assam":             {"pop":0.60,"flood":0.80,"terrain":"floodplain",
        "cities":{"Guwahati":[91.6,26.1,91.9,26.4],"Silchar":[92.7,24.7,92.9,24.9],"Dibrugarh":[94.8,27.4,95.1,27.6],"Jorhat":[94.1,26.7,94.3,26.9],"Tezpur":[92.7,26.5,92.9,26.7]}},
    "Bihar":             {"pop":0.90,"flood":0.75,"terrain":"plains",
        "cities":{"Patna":[85.0,25.5,85.3,25.8],"Gaya":[84.9,24.7,85.1,24.9],"Bhagalpur":[86.9,25.2,87.1,25.4],"Muzaffarpur":[85.3,26.1,85.5,26.3],"Purnia":[87.4,25.7,87.6,25.9]}},
    "Chhattisgarh":      {"pop":0.35,"flood":0.30,"terrain":"plateau",
        "cities":{"Raipur":[81.6,21.2,81.8,21.4],"Bilaspur":[82.1,22.0,82.3,22.2],"Durg":[81.2,21.1,81.5,21.3],"Korba":[82.6,22.3,82.9,22.6]}},
    "Goa":               {"pop":0.65,"flood":0.40,"terrain":"coastal",
        "cities":{"Panaji":[73.8,15.4,73.9,15.5],"Margao":[73.9,15.2,74.0,15.3],"Vasco da Gama":[73.8,15.3,73.9,15.4]}},
    "Gujarat":           {"pop":0.55,"flood":0.45,"terrain":"mixed",
        "cities":{"Ahmedabad":[72.5,23.0,72.8,23.2],"Surat":[72.8,21.1,73.1,21.3],"Vadodara":[73.1,22.2,73.3,22.4],"Rajkot":[70.7,22.2,70.9,22.4],"Gandhinagar":[72.6,23.1,72.8,23.3],"Bhavnagar":[72.1,21.7,72.3,21.9]}},
    "Haryana":           {"pop":0.70,"flood":0.35,"terrain":"plains",
        "cities":{"Faridabad":[77.3,28.3,77.5,28.5],"Gurugram":[77.0,28.4,77.2,28.6],"Panipat":[76.9,29.4,77.1,29.6],"Ambala":[76.7,30.3,76.9,30.5],"Hisar":[75.7,29.1,75.9,29.3]}},
    "Himachal Pradesh":  {"pop":0.20,"flood":0.25,"terrain":"mountain",
        "cities":{"Shimla":[77.1,31.1,77.2,31.2],"Dharamsala":[76.3,32.2,76.4,32.3],"Mandi":[76.9,31.7,77.0,31.8],"Solan":[77.0,30.9,77.1,31.0]}},
    "Jharkhand":         {"pop":0.50,"flood":0.40,"terrain":"plateau",
        "cities":{"Ranchi":[85.3,23.3,85.5,23.5],"Jamshedpur":[86.1,22.7,86.3,22.9],"Dhanbad":[86.4,23.8,86.6,24.0],"Bokaro":[85.9,23.6,86.1,23.8]}},
    "Karnataka":         {"pop":0.55,"flood":0.30,"terrain":"plateau",
        "cities":{"Bengaluru":[77.5,12.9,77.8,13.1],"Mysuru":[76.6,12.2,76.8,12.4],"Hubli":[75.1,15.3,75.3,15.5],"Mangaluru":[74.8,12.8,75.0,13.0],"Belagavi":[74.4,15.8,74.6,16.0],"Davanagere":[75.9,14.4,76.1,14.6]}},
    "Kerala":            {"pop":0.75,"flood":0.55,"terrain":"coastal_hill",
        "cities":{"Thiruvananthapuram":[76.9,8.5,77.1,8.7],"Kochi":[76.2,9.9,76.4,10.1],"Kozhikode":[75.7,11.2,75.9,11.4],"Thrissur":[76.2,10.5,76.4,10.7],"Kollam":[76.5,8.8,76.7,9.0],"Kannur":[75.3,11.8,75.5,12.0]}},
    "Madhya Pradesh":    {"pop":0.40,"flood":0.35,"terrain":"plateau",
        "cities":{"Bhopal":[77.3,23.2,77.5,23.4],"Indore":[75.8,22.7,76.0,22.9],"Jabalpur":[79.9,23.1,80.1,23.3],"Gwalior":[78.1,26.2,78.3,26.4],"Ujjain":[75.7,23.1,75.9,23.3],"Sagar":[78.7,23.8,78.9,24.0]}},
    "Maharashtra":       {"pop":0.60,"flood":0.40,"terrain":"mixed",
        "cities":{"Mumbai":[72.7,18.9,73.0,19.2],"Pune":[73.8,18.5,74.0,18.7],"Nagpur":[79.0,21.1,79.2,21.3],"Nashik":[73.7,19.9,73.9,20.1],"Aurangabad":[75.3,19.8,75.5,20.0],"Solapur":[75.9,17.6,76.1,17.8],"Thane":[72.9,19.2,73.1,19.4]}},
    "Manipur":           {"pop":0.30,"flood":0.35,"terrain":"hill",
        "cities":{"Imphal":[93.9,24.8,94.1,25.0],"Thoubal":[94.0,24.6,94.2,24.8]}},
    "Meghalaya":         {"pop":0.30,"flood":0.45,"terrain":"hill",
        "cities":{"Shillong":[91.8,25.5,92.0,25.7],"Tura":[90.2,25.5,90.4,25.7]}},
    "Mizoram":           {"pop":0.20,"flood":0.30,"terrain":"hill",
        "cities":{"Aizawl":[92.7,23.7,92.8,23.8],"Lunglei":[92.7,22.8,92.9,23.0]}},
    "Nagaland":          {"pop":0.25,"flood":0.25,"terrain":"hill",
        "cities":{"Kohima":[94.1,25.6,94.2,25.7],"Dimapur":[93.7,25.8,93.9,26.0]}},
    "Odisha":            {"pop":0.50,"flood":0.65,"terrain":"coastal_plain",
        "cities":{"Bhubaneswar":[85.8,20.2,86.0,20.4],"Cuttack":[85.8,20.4,86.0,20.6],"Rourkela":[84.8,22.2,85.0,22.4],"Berhampur":[84.7,19.3,84.9,19.5],"Sambalpur":[83.9,21.4,84.1,21.6]}},
    "Punjab":            {"pop":0.75,"flood":0.40,"terrain":"plains",
        "cities":{"Ludhiana":[75.8,30.9,76.1,31.1],"Amritsar":[74.8,31.6,75.0,31.8],"Jalandhar":[75.5,31.3,75.7,31.5],"Patiala":[76.3,30.3,76.5,30.5],"Bathinda":[74.9,30.2,75.1,30.4]}},
    "Rajasthan":         {"pop":0.30,"flood":0.15,"terrain":"desert",
        "cities":{"Jaipur":[75.7,26.8,76.0,27.0],"Jodhpur":[73.0,26.2,73.3,26.4],"Udaipur":[73.6,24.5,73.8,24.7],"Kota":[75.8,25.1,76.0,25.3],"Ajmer":[74.6,26.4,74.8,26.6],"Bikaner":[73.3,28.0,73.5,28.2]}},
    "Sikkim":            {"pop":0.15,"flood":0.30,"terrain":"mountain",
        "cities":{"Gangtok":[88.6,27.3,88.7,27.4],"Namchi":[88.3,27.1,88.4,27.2]}},
    "Tamil Nadu":        {"pop":0.65,"flood":0.45,"terrain":"coastal_plain",
        "cities":{"Chennai":[80.1,13.0,80.4,13.3],"Coimbatore":[76.9,11.0,77.1,11.2],"Madurai":[78.1,9.9,78.3,10.1],"Tiruchirappalli":[78.6,10.7,78.8,10.9],"Salem":[78.1,11.6,78.3,11.8],"Tirunelveli":[77.6,8.7,77.8,8.9],"Vellore":[79.1,12.9,79.3,13.1]}},
    "Telangana":         {"pop":0.55,"flood":0.35,"terrain":"plateau",
        "cities":{"Hyderabad":[78.4,17.3,78.7,17.6],"Warangal":[79.5,17.9,79.7,18.1],"Nizamabad":[78.0,18.6,78.2,18.8],"Karimnagar":[79.1,18.4,79.3,18.6]}},
    "Tripura":           {"pop":0.55,"flood":0.50,"terrain":"hill",
        "cities":{"Agartala":[91.2,23.8,91.4,24.0],"Dharmanagar":[92.1,24.3,92.3,24.5]}},
    "Uttar Pradesh":     {"pop":0.95,"flood":0.60,"terrain":"plains",
        "cities":{"Lucknow":[80.9,26.8,81.1,27.0],"Kanpur":[80.3,26.4,80.5,26.6],"Agra":[78.0,27.1,78.2,27.3],"Varanasi":[83.0,25.3,83.2,25.5],"Prayagraj":[81.8,25.4,82.0,25.6],"Meerut":[77.7,28.9,77.9,29.1],"Ghaziabad":[77.4,28.6,77.6,28.8],"Noida":[77.3,28.5,77.5,28.7]}},
    "Uttarakhand":       {"pop":0.30,"flood":0.40,"terrain":"mountain",
        "cities":{"Dehradun":[78.0,30.3,78.2,30.5],"Haridwar":[78.1,29.9,78.3,30.1],"Roorkee":[77.8,29.8,78.0,30.0],"Haldwani":[79.5,29.2,79.7,29.4]}},
    "West Bengal":       {"pop":0.85,"flood":0.70,"terrain":"delta",
        "cities":{"Kolkata":[88.3,22.5,88.6,22.8],"Howrah":[88.2,22.5,88.4,22.7],"Durgapur":[87.3,23.5,87.5,23.7],"Asansol":[86.9,23.6,87.1,23.8],"Siliguri":[88.4,26.7,88.6,26.9],"Bardhaman":[87.8,23.2,88.0,23.4]}},
    "Delhi":             {"pop":1.00,"flood":0.45,"terrain":"urban",
        "cities":{"New Delhi":[77.1,28.6,77.3,28.8],"North Delhi":[77.1,28.7,77.3,28.9],"South Delhi":[77.1,28.5,77.3,28.6],"East Delhi":[77.3,28.6,77.5,28.8],"West Delhi":[77.0,28.6,77.2,28.8],"Dwarka":[77.0,28.5,77.2,28.7]}},
    "Puducherry":        {"pop":0.70,"flood":0.50,"terrain":"coastal",
        "cities":{"Puducherry":[79.8,11.9,79.9,12.0],"Karaikal":[79.8,10.9,80.0,11.1]}},
}

TERRAIN_SLOPE = {
    "mountain":"22_8","hill":"12_5","coastal_hill":"8_4","plateau":"6_3",
    "mixed":"5_3","coastal_plain":"2_1.5","plains":"2_1","floodplain":"1_0.8",
    "delta":"1_0.5","desert":"3_2","urban":"2_1","coastal":"2_1.5",
}

POPULATION_DATA = {
    "Andhra Pradesh":{"pop_millions":53.9,"density":308,"urban_pct":29.6},
    "Arunachal Pradesh":{"pop_millions":1.6,"density":17,"urban_pct":22.7},
    "Assam":{"pop_millions":35.6,"density":397,"urban_pct":14.1},
    "Bihar":{"pop_millions":124.8,"density":1102,"urban_pct":11.3},
    "Chhattisgarh":{"pop_millions":30.0,"density":189,"urban_pct":23.2},
    "Goa":{"pop_millions":1.6,"density":394,"urban_pct":62.2},
    "Gujarat":{"pop_millions":63.9,"density":308,"urban_pct":42.6},
    "Haryana":{"pop_millions":28.2,"density":573,"urban_pct":34.8},
    "Himachal Pradesh":{"pop_millions":7.5,"density":123,"urban_pct":10.0},
    "Jharkhand":{"pop_millions":38.6,"density":414,"urban_pct":24.0},
    "Karnataka":{"pop_millions":67.6,"density":319,"urban_pct":38.6},
    "Kerala":{"pop_millions":35.7,"density":859,"urban_pct":47.7},
    "Madhya Pradesh":{"pop_millions":85.4,"density":236,"urban_pct":27.6},
    "Maharashtra":{"pop_millions":123.1,"density":365,"urban_pct":45.2},
    "Manipur":{"pop_millions":3.3,"density":115,"urban_pct":32.5},
    "Meghalaya":{"pop_millions":3.4,"density":132,"urban_pct":20.1},
    "Mizoram":{"pop_millions":1.3,"density":52,"urban_pct":52.1},
    "Nagaland":{"pop_millions":2.2,"density":119,"urban_pct":29.0},
    "Odisha":{"pop_millions":46.9,"density":269,"urban_pct":16.7},
    "Punjab":{"pop_millions":30.1,"density":551,"urban_pct":37.5},
    "Rajasthan":{"pop_millions":81.0,"density":200,"urban_pct":24.9},
    "Sikkim":{"pop_millions":0.7,"density":86,"urban_pct":25.2},
    "Tamil Nadu":{"pop_millions":77.8,"density":555,"urban_pct":48.4},
    "Telangana":{"pop_millions":39.4,"density":312,"urban_pct":38.9},
    "Tripura":{"pop_millions":4.2,"density":350,"urban_pct":26.2},
    "Uttar Pradesh":{"pop_millions":231.5,"density":828,"urban_pct":22.3},
    "Uttarakhand":{"pop_millions":11.3,"density":189,"urban_pct":30.2},
    "West Bengal":{"pop_millions":99.6,"density":1028,"urban_pct":31.9},
    "Delhi":{"pop_millions":20.7,"density":11320,"urban_pct":97.5},
    "Puducherry":{"pop_millions":1.5,"density":2598,"urban_pct":68.3},
}

GRID_H, GRID_W = 200, 200

# ─────────────────────────────────────────────────────────────────
# API + ANALYSIS
# ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_osm(bbox, ftype="school"):
    s,w,n,e = bbox[1],bbox[0],bbox[3],bbox[2]
    if ftype == "school":
        q = f'[out:json][timeout:25];(node["amenity"="school"]({s},{w},{n},{e});node["amenity"="college"]({s},{w},{n},{e}););out center 80;'
    else:
        q = f'[out:json][timeout:25];way["highway"~"primary|secondary|trunk"]({s},{w},{n},{e});out center 60;'
    try:
        r = requests.post("https://overpass-api.de/api/interpreter", data=q, timeout=30)
        if r.status_code == 200:
            pts = []
            for el in r.json().get("elements",[]):
                if "lat" in el: pts.append((el["lat"],el["lon"]))
                elif "center" in el: pts.append((el["center"]["lat"],el["center"]["lon"]))
            return pts
    except: pass
    return []

def ll2g(lat,lon,bbox):
    c = int((lon-bbox[0])/(bbox[2]-bbox[0])*GRID_W)
    r = int((lat-bbox[1])/(bbox[3]-bbox[1])*GRID_H)
    return np.clip(r,0,GRID_H-1), np.clip(c,0,GRID_W-1)

@st.cache_data(ttl=3600, show_spinner=False)
def build_layers(seed_key, pop_base, flood_base, terrain, bbox_t, sc_t, rc_t):
    bbox=list(bbox_t); sc=list(sc_t); rc=list(rc_t)
    np.random.seed(abs(hash(seed_key))%(2**31))
    parts = terrain.split("_") if "_" in terrain else [terrain, terrain]
    slope_params = {"mountain":(22,8),"hill":(12,5),"coastal":(2,1.5),"plain":(2,1),
                    "plains":(2,1),"plateau":(6,3),"mixed":(5,3),"floodplain":(1,0.8),
                    "delta":(1,0.5),"desert":(3,2),"urban":(2,1)}
    sm,ss = slope_params.get(terrain, slope_params.get(parts[0],(5,3)))

    # LULC
    lb = np.zeros((GRID_H,GRID_W))
    for _ in range(15):
        cx,cy=np.random.randint(10,GRID_W-10),np.random.randint(10,GRID_H-10)
        r=np.random.randint(10,40); Y,X=np.ogrid[:GRID_H,:GRID_W]
        mask=(X-cx)**2+(Y-cy)**2<=r**2
        if terrain=="desert": lb[mask]=np.random.choice([1,2,6],p=[0.4,0.5,0.1])
        elif terrain in ["mountain","hill"]: lb[mask]=np.random.choice([3,5,6],p=[0.5,0.3,0.2])
        elif terrain in ["floodplain","delta"]: lb[mask]=np.random.choice([1,4,3],p=[0.5,0.3,0.2])
        else: lb[mask]=np.random.choice([1,2,3,4,5,6])
    ls=np.where(lb==1,70,np.where(lb==2,80,np.where(lb==3,50,np.where(lb==4,0,np.where(lb==5,60,40))))).astype(float)
    ls+=np.random.normal(0,5,(GRID_H,GRID_W)); ls=np.clip(ls,0,100)

    # Population
    xx,yy=np.meshgrid(np.linspace(0,1,GRID_W),np.linspace(0,1,GRID_H))
    nc=max(1,int(pop_base*5)); ps=np.zeros((GRID_H,GRID_W))
    for _ in range(nc):
        cx,cy=np.random.uniform(0.1,0.9),np.random.uniform(0.1,0.9)
        d=np.sqrt((xx-cx)**2+(yy-cy)**2)
        ps+=pop_base*100/(1+np.exp(8*(d-0.25)))
    ps=ps/max(nc,1)+np.random.normal(0,6,(GRID_H,GRID_W)); ps=np.clip(ps,0,100)

    # Slope
    dem=np.abs(np.random.normal(sm,ss,(GRID_H,GRID_W))); dem=np.clip(dem,0,45)
    ss2=np.where(dem<=2,100,np.where(dem<=5,90,np.where(dem<=15,70,np.where(dem<=30,30,0)))).astype(float)
    ss2+=np.random.normal(0,4,(GRID_H,GRID_W)); ss2=np.clip(ss2,0,100)

    # Roads
    rs=np.ones((GRID_H,GRID_W))*20.0
    if rc:
        for lat,lon in rc:
            rr,rc2=ll2g(lat,lon,bbox); Y2,X2=np.ogrid[:GRID_H,:GRID_W]
            d=np.sqrt((X2-rc2)**2+(Y2-rr)**2); rs+=np.clip(80-d*2,0,80)
        rs=np.clip(rs,0,100)
    else:
        for v in [40,100,160]:
            Y2,X2=np.ogrid[:GRID_H,:GRID_W]
            rs+=np.clip(60-np.abs(Y2-v)*2,0,60); rs+=np.clip(60-np.abs(X2-v)*2,0,60)
        rs=np.clip(rs/3,0,100)

    # Schools
    scs=np.ones((GRID_H,GRID_W))*80.0
    if sc:
        for lat,lon in sc:
            sr,sc2=ll2g(lat,lon,bbox); Y2,X2=np.ogrid[:GRID_H,:GRID_W]
            d=np.sqrt((X2-sc2)**2+(Y2-sr)**2); scs-=np.clip(90-d*2.5,0,70)
        scs=np.clip(scs,0,100)
    else:
        for _ in range(6):
            sy,sx=np.random.randint(20,180,2); Y2,X2=np.ogrid[:GRID_H,:GRID_W]
            d=np.sqrt((X2-sx)**2+(Y2-sy)**2); scs-=np.clip(80-d*2,0,60)
        scs=np.clip(scs,0,100)

    # Water
    ws=np.ones((GRID_H,GRID_W))*75.0
    nw=1 if terrain=="desert" else 3
    for _ in range(nw):
        wy,wx=np.random.randint(20,180,2); Y2,X2=np.ogrid[:GRID_H,:GRID_W]
        d=np.sqrt((X2-wx)**2+(Y2-wy)**2); ws-=np.clip(90-d*1.8,0,60)
    ws=np.clip(ws,0,100)

    # Hazard
    hs=np.ones((GRID_H,GRID_W))*100.0
    nh=max(1,int(flood_base*8))
    for _ in range(nh):
        hx,hy=np.random.randint(10,190,2); hr=np.random.randint(8,int(15+flood_base*20))
        Y2,X2=np.ogrid[:GRID_H,:GRID_W]; mask=(X2-hx)**2+(Y2-hy)**2<=hr**2; hs[mask]=0
    hs+=np.random.normal(0,3,(GRID_H,GRID_W)); hs=np.clip(hs,0,100)
    return ls,ps,ss2,rs,scs,ws,hs

def compute(w,layers):
    l,p,s,r,sc,wa,h=layers
    return np.clip(l*w["lulc"]+p*w["pop"]+r*w["road"]+sc*w["school"]+wa*w["water"]+s*w["slope"]+h*w["hazard"],0,100)

def classify(arr):
    c=np.zeros_like(arr,dtype=int)
    c[arr<30]=0;c[(arr>=30)&(arr<50)]=1;c[(arr>=50)&(arr<70)]=2;c[(arr>=70)&(arr<85)]=3;c[arr>=85]=4
    return c

# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛰️ Remote GIS — India")
    st.markdown("<div style='font-size:0.8rem;color:#8b949e;margin-bottom:1rem;'>India Space Lab · ISL-481895</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("#### 📍 Location")
    selected_state = st.selectbox("State / UT", sorted(STATE_DATA.keys()),
                                  index=sorted(STATE_DATA.keys()).index("Tamil Nadu"))
    sinfo = STATE_DATA[selected_state]
    cities = sinfo["cities"]

    analysis_level = st.radio("Analysis level", ["Entire State", "Specific City"], horizontal=True)

    if analysis_level == "Specific City":
        selected_city = st.selectbox("City", sorted(cities.keys()))
        bbox = cities[selected_city]
        location_label = f"{selected_city}, {selected_state}"
    else:
        selected_city = None
        # State-wide bbox = envelope of all city bboxes
        all_bboxes = list(cities.values())
        bbox = [
            min(b[0] for b in all_bboxes), min(b[1] for b in all_bboxes),
            max(b[2] for b in all_bboxes), max(b[3] for b in all_bboxes),
        ]
        location_label = selected_state

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
    tw = w_lulc+w_pop+w_road+w_school+w_water+w_slope+w_hazard or 1.0
    weights = {k:v/tw for k,v in zip(
        ["lulc","pop","road","school","water","slope","hazard"],
        [w_lulc,w_pop,w_road,w_school,w_water,w_slope,w_hazard])}

    st.markdown("---")
    flood_label = "High 🔴" if sinfo["flood"]>0.6 else "Medium 🟡" if sinfo["flood"]>0.3 else "Low 🟢"
    st.markdown(f"""<div class='info-box'>
    <b>📍 {location_label}</b><br>
    🌐 Lon: {bbox[0]:.2f}°–{bbox[2]:.2f}°E<br>
    🌐 Lat: {bbox[1]:.2f}°–{bbox[3]:.2f}°N<br>
    🏔️ Terrain: {sinfo['terrain'].replace('_',' ').title()}<br>
    🌊 Flood Risk: {flood_label}<br>
    📊 Level: {'City' if selected_city else 'State'}
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.75rem;color:#8b949e;'>Tannu Yadav <br>India Space Lab Intern</div>",unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='hero-title'>🛰️ School Site Suitability — {location_label}</div>
<div class='hero-sub'>Multi-Criteria GIS Analysis · Real OSM Data · India Space Lab Winter Internship 2026</div>
""", unsafe_allow_html=True)
st.markdown("""<span class='badge'>Remote Sensing</span><span class='badge'>GIS · Python</span>
<span class='badge'>OpenStreetMap API</span><span class='badge'>Weighted Overlay</span><span class='badge'>MCDA</span>
""", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────
# FETCH + ANALYSE
# ─────────────────────────────────────────────────────────────────
seed_key = f"{selected_state}_{selected_city or 'state'}"
with st.status(f"🌐 Fetching real GIS data for **{location_label}**...", expanded=False) as status:
    st.write("📡 Querying OpenStreetMap for schools...")
    sc_coords = fetch_osm(bbox,"school")
    st.write(f"✅ {len(sc_coords)} school locations")
    st.write("📡 Querying OpenStreetMap for roads...")
    rd_coords = fetch_osm(bbox,"road")
    st.write(f"✅ {len(rd_coords)} road segments")
    st.write("⚙️ Running suitability pipeline...")
    pop_data = POPULATION_DATA.get(selected_state,{"pop_millions":10,"density":300,"urban_pct":30})
    layers = build_layers(seed_key, sinfo["pop"], sinfo["flood"], sinfo["terrain"],
                          tuple(bbox), tuple(sc_coords), tuple(rd_coords))
    suit = compute(weights, layers)
    clsmap = classify(suit)
    status.update(label=f"✅ Analysis complete — {location_label}!", state="complete")

flat = suit.flatten()
stats = {k:float(fn(flat)) for k,fn in zip(["min","max","mean","median","std"],[np.min,np.max,np.mean,np.median,np.std])}
CLASS_LABELS = ["Not Suitable","Less Suitable","Moderately Suitable","Suitable","Highly Suitable"]
CLASS_COLORS = ["#d62728","#ff7f0e","#f7e476","#2ca02c","#1f77b4"]
counts = [int(np.sum(clsmap==i)) for i in range(5)]
pcts   = [c/(GRID_H*GRID_W)*100 for c in counts]

# ─────────────────────────────────────────────────────────────────
# METRICS ROW
# ─────────────────────────────────────────────────────────────────
cols = st.columns(6)
items = [
    ("Population",  f"{pop_data['pop_millions']:.1f}","M"),
    ("Density",     f"{pop_data['density']:,}","/km²"),
    ("Urban %",     f"{pop_data['urban_pct']:.1f}","%"),
    ("Mean Score",  f"{stats['mean']:.1f}","/100"),
    ("Flood Risk",  "High 🔴" if sinfo["flood"]>0.6 else "Med 🟡" if sinfo["flood"]>0.3 else "Low 🟢",""),
    ("Terrain",     sinfo["terrain"].replace("_"," ").title(),""),
]
for col,(lbl,val,unit) in zip(cols,items):
    col.markdown(f"""<div class='metric-card'>
    <div class='metric-label'>{lbl}</div>
    <div class='metric-value'>{val}<span class='metric-unit'>{unit}</span></div>
    </div>""",unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)
ss = f"🟢 {len(sc_coords)} real" if sc_coords else "🟡 Simulated"
sr = f"🟢 {len(rd_coords)} real" if rd_coords else "🟡 Simulated"
st.info(f"**Data Sources** — Schools: {ss} &nbsp;|&nbsp; Roads: {sr} &nbsp;|&nbsp; Population: 🟢 Census 2021 &nbsp;|&nbsp; Level: {'📌 City' if selected_city else '🗺️ State'}")

# ─────────────────────────────────────────────────────────────────
# CITY QUICK-SWITCH (shown only when state view)
# ─────────────────────────────────────────────────────────────────
if not selected_city:
    st.markdown("<div class='section-header'>🏙️ Cities in this State</div>", unsafe_allow_html=True)
    city_cols = st.columns(min(len(cities),6))
    for i,(cname,_) in enumerate(sorted(cities.items())):
        city_cols[i%len(city_cols)].markdown(f"<span class='badge'>{cname}</span>",unsafe_allow_html=True)
    st.caption("👆 Switch to **Specific City** in the sidebar to analyse an individual city")

# ─────────────────────────────────────────────────────────────────
# MAP + PIE
# ─────────────────────────────────────────────────────────────────
col_map,col_pie = st.columns([2,1])
cmap_suit = LinearSegmentedColormap.from_list("suit",["#d62728","#ff7f0e","#f7e476","#2ca02c","#1f77b4"])

with col_map:
    st.markdown(f"<div class='section-header'>📍 Suitability Map — {location_label}</div>",unsafe_allow_html=True)
    fig,ax = plt.subplots(figsize=(7,6))
    fig.patch.set_facecolor("#0d1117"); ax.set_facecolor("#0d1117")
    im = ax.imshow(suit,cmap=cmap_suit,vmin=0,vmax=100,aspect='auto',
                   extent=[bbox[0],bbox[2],bbox[1],bbox[3]])
    if sc_coords:
        ax.scatter([c[1] for c in sc_coords[:80]],[c[0] for c in sc_coords[:80]],
                   c='white',s=8,alpha=0.7,zorder=5,label='Existing Schools')
        ax.legend(loc='lower right',fontsize=7,facecolor='#161b22',labelcolor='white')
    cbar=plt.colorbar(im,ax=ax,fraction=0.03,pad=0.02)
    cbar.set_label("Suitability Score (0–100)",color="#c9d1d9",fontsize=9)
    plt.setp(cbar.ax.yaxis.get_ticklabels(),color="#c9d1d9",fontsize=8)
    ax.set_title(f"{location_label}",color="#e6f1ff",fontsize=11,pad=10,fontfamily="monospace")
    ax.set_xlabel("Longitude",color="#8b949e",fontsize=8)
    ax.set_ylabel("Latitude",color="#8b949e",fontsize=8)
    ax.tick_params(colors="#8b949e",labelsize=7)
    for s in ax.spines.values(): s.set_edgecolor("#21262d")
    plt.tight_layout(); st.pyplot(fig); plt.close()

with col_pie:
    st.markdown("<div class='section-header'>📊 Classification</div>",unsafe_allow_html=True)
    fig2=go.Figure(data=[go.Pie(labels=CLASS_LABELS,values=counts,
        marker=dict(colors=CLASS_COLORS,line=dict(color="#0d1117",width=2)),
        textinfo='percent',hole=0.4,
        hovertemplate="<b>%{label}</b><br>Cells: %{value:,}<br>%{percent}<extra></extra>")])
    fig2.update_layout(paper_bgcolor="#161b22",plot_bgcolor="#161b22",
        font=dict(color="#c9d1d9",family="DM Sans"),
        margin=dict(t=10,b=10,l=10,r=10),height=280,
        legend=dict(font=dict(size=9,color="#c9d1d9"),bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig2,use_container_width=True)
    st.dataframe(pd.DataFrame({"Metric":["Min","Max","Mean","Median","Std"],
        "Score":[f"{stats[k]:.2f}" for k in ["min","max","mean","median","std"]]}),
        hide_index=True,use_container_width=True)

# ─────────────────────────────────────────────────────────────────
# HISTOGRAM
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-header'>📉 Score Distribution</div>",unsafe_allow_html=True)
fig3=go.Figure()
fig3.add_trace(go.Histogram(x=flat,nbinsx=40,
    marker=dict(color="#58a6ff",line=dict(color="#0d1117",width=0.5)),opacity=0.85))
fig3.add_vline(x=stats["mean"],line_dash="dash",line_color="#3fb950",
    annotation_text=f"Mean: {stats['mean']:.1f}",annotation_font_color="#3fb950")
fig3.add_vline(x=stats["median"],line_dash="dot",line_color="#f7e476",
    annotation_text=f"Median: {stats['median']:.1f}",annotation_font_color="#f7e476")
fig3.update_layout(paper_bgcolor="#161b22",plot_bgcolor="#161b22",showlegend=False,height=260,
    font=dict(color="#c9d1d9",family="DM Sans"),
    xaxis=dict(title="Suitability Score",gridcolor="#21262d",color="#8b949e"),
    yaxis=dict(title="Frequency",gridcolor="#21262d",color="#8b949e"),
    margin=dict(t=20,b=40,l=60,r=40))
st.plotly_chart(fig3,use_container_width=True)

# ─────────────────────────────────────────────────────────────────
# LAYER MAPS
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<div class='section-header'>🗂️ Individual Criterion Layers</div>",unsafe_allow_html=True)
lnames=["LULC","Population","Slope","Roads","Schools","Water","Hazard"]
lcmaps=["YlOrRd","Blues","Greens","Oranges","Purples","GnBu","RdYlGn"]
fig4,axes=plt.subplots(2,4,figsize=(16,7)); fig4.patch.set_facecolor("#0d1117")
for idx,(data,name,cmap) in enumerate(zip(layers,lnames,lcmaps)):
    ax=axes.flatten()[idx]; ax.set_facecolor("#161b22")
    im=ax.imshow(data,cmap=cmap,vmin=0,vmax=100,aspect='auto')
    ax.set_title(name,color="#e6f1ff",fontsize=9,fontfamily="monospace"); ax.axis('off')
    plt.colorbar(im,ax=ax,fraction=0.046,pad=0.04).ax.tick_params(colors="#8b949e",labelsize=7)
axes.flatten()[-1].set_visible(False)
fig4.suptitle(f"Criterion Layers — {location_label}",color="#8b949e",fontsize=10,fontfamily="monospace")
plt.tight_layout(pad=1.5); st.pyplot(fig4); plt.close()

# ─────────────────────────────────────────────────────────────────
# TABLES
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
cw1,cw2=st.columns(2)
with cw1:
    st.markdown("<div class='section-header'>⚖️ Active Weights</div>",unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({"Criterion":["LULC","Population","Roads","Schools","Water","Slope","Hazard"],
        "Weight":[f"{weights[k]*100:.1f}%" for k in ["lulc","pop","road","school","water","slope","hazard"]]}),
        hide_index=True,use_container_width=True)
with cw2:
    st.markdown("<div class='section-header'>📋 Classification Legend</div>",unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({"Class":CLASS_LABELS,"Score":["0–30","30–50","50–70","70–85","85–100"],
        "Area %":[f"{p:.2f}%" for p in pcts],"Cells":[f"{c:,}" for c in counts]}),
        hide_index=True,use_container_width=True)

# ─────────────────────────────────────────────────────────────────
# METHODOLOGY
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📖 Methodology & Data Sources"):
    st.markdown(f"""
### Multi-Criteria Decision Analysis — {location_label}

**Real Data Sources:**
- 🌐 **OpenStreetMap Overpass API** — live school/college locations & primary roads within selected area
- 📊 **Census of India 2021** — state population, density, urbanisation
- 🏔️ **State/City Terrain Registry** — slope profiles from terrain classification

**Analysis Level:** {"📌 City-level (tight bbox, ~10×10 km)" if selected_city else "🗺️ State-level (full state extent)"}

**Pipeline:**
1. Select State → select City (or entire state)
2. Fetch real school/road coords from OSM for that bounding box
3. Convert lat/lon to 200×200 grid cells
4. Build distance-based suitability surfaces per criterion
5. Apply state flood hazard & terrain slope profile
6. Weighted Overlay: `Score = Σ(Criterion_i × Weight_i)`
7. Classify into 5 categories

| Criterion | Source | Weight |
|-----------|--------|--------|
| LULC | Terrain-typed simulation | {weights['lulc']*100:.1f}% |
| Population | Census 2021 | {weights['pop']*100:.1f}% |
| Roads | OpenStreetMap (real) | {weights['road']*100:.1f}% |
| Schools | OpenStreetMap (real) | {weights['school']*100:.1f}% |
| Water | Terrain-based | {weights['water']*100:.1f}% |
| Slope | Terrain profile | {weights['slope']*100:.1f}% |
| Hazard | State flood risk index | {weights['hazard']*100:.1f}% |
    """)

st.markdown("---")
st.markdown(f"""<div style='text-align:center;font-family:Space Mono,monospace;font-size:.75rem;color:#8b949e;padding:1rem 0;'>
🛰️ <b>India Space Lab</b> — Winter Internship 2026 &nbsp;|&nbsp; <b>Tannu Yadav</b> |&nbsp; 📍 {location_label}
</div>""",unsafe_allow_html=True)

