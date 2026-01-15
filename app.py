import streamlit as st
import pydeck as pdk

# --- 1. DATA: STATIONS & COORDINATES ---
station_coords = {
    "Wimco Nagar": [13.1725, 80.3069], "Kaladipet": [13.1648, 80.3033], "Tollgate": [13.1554, 80.2987],
    "New Washermanpet": [13.1432, 80.2917], "Tondiarpet": [13.1360, 80.2870], "Sir Theagaraya College": [13.1275, 80.2845],
    "Washermanpet": [13.1148, 80.2872], "Mannadi": [13.0928, 80.2893], "High Court": [13.0877, 80.2865],
    "Central Metro": [13.0814, 80.2727], "Government Estate": [13.0694, 80.2743], "LIC": [13.0645, 80.2687],
    "Thousand Lights": [13.0583, 80.2580], "AG-DMS": [13.0494, 80.2505], "Teynampet": [13.0425, 80.2483],
    "Nandanam": [13.0335, 80.2405], "Saidapet": [13.0245, 80.2245], "Little Mount": [13.0180, 80.2205],
    "Guindy": [13.0093, 80.2206], "Alandur": [12.9975, 80.2006], "Nanganallur Road": [12.9880, 80.1905],
    "Meenambakkam": [12.9805, 80.1805], "Chennai Airport": [12.9800, 80.1633],
    "Egmore": [13.0732, 80.2609], "Nehru Park": [13.0765, 80.2500], "Kilpauk": [13.0785, 80.2425],
    "Pachaiyappa College": [13.0795, 80.2300], "Shenoy Nagar": [13.0820, 80.2225], "Anna Nagar East": [13.0850, 80.2101],
    "Anna Nagar Tower": [13.0875, 80.2050], "Thirumangalam": [13.0890, 80.1950], "Koyambedu": [13.0735, 80.1948],
    "CMBT": [13.0695, 80.2050], "Arumbakkam": [13.0620, 80.2110], "Vadapalani": [13.0500, 80.2120],
    "Ashok Nagar": [13.0373, 80.2123], "Ekkattuthangal": [13.0255, 80.2055], "St Thomas Mount": [13.0050, 80.1980]
}

blue_line = [
    'Wimco Nagar', 'Kaladipet', 'Tollgate', 'New Washermanpet', 'Tondiarpet', 
    'Sir Theagaraya College', 'Washermanpet', 'Mannadi', 'High Court', 
    'Central Metro', 'Government Estate', 'LIC', 'Thousand Lights', 'AG-DMS', 
    'Teynampet', 'Nandanam', 'Saidapet', 'Little Mount', 'Guindy', 'Alandur', 
    'Nanganallur Road', 'Meenambakkam', 'Chennai Airport'
]

green_line = [
    'Central Metro', 'Egmore', 'Nehru Park', 'Kilpauk', 'Pachaiyappa College', 
    'Shenoy Nagar', 'Anna Nagar East', 'Anna Nagar Tower', 'Thirumangalam', 
    'Koyambedu', 'CMBT', 'Arumbakkam', 'Vadapalani', 'Ashok Nagar', 
    'Ekkattuthangal', 'Alandur', 'St Thomas Mount'
]

all_stations = sorted(list(station_coords.keys()))

# --- 2. LOGIC ---
def get_path_segment(line, start, end):
    if start not in line or end not in line: return []
    idx_s = line.index(start)
    idx_e = line.index(end)
    return line[idx_s : idx_e + 1] if idx_s < idx_e else line[idx_e : idx_s + 1][::-1]

def get_full_route(start, end):
    start_blue, end_blue = start in blue_line, end in blue_line
    start_green, end_green = start in green_line, end in green_line

    if (start_blue and end_blue) and not (start_green and end_green):
        return get_path_segment(blue_line, start, end), "Direct (Blue Line)"
    if (start_green and end_green) and not (start_blue and end_blue):
        return get_path_segment(green_line, start, end), "Direct (Green Line)"
    
    interchanges = ['Alandur', 'Central Metro']
    min_len, best_path, switch_at = 100, [], ""

    for x in interchanges:
        line1 = blue_line if start_blue else green_line
        line2 = blue_line if x in blue_line else green_line 
        if x not in line1: line1 = green_line
        if x not in line2: line2 = green_line

        leg1 = get_path_segment(line1, start, x)
        leg2 = get_path_segment(line2, x, end)
        
        if leg1 and leg2:
            full = leg1 + leg2[1:]
            if len(full) < min_len:
                min_len = len(full)
                best_path = full
                switch_at = x
                
    return best_path, f"Switch at {switch_at}"

# --- 3. UI SETUP ---
st.set_page_config(page_title="Chennai Metro", page_icon="🚇", layout="wide")
st.title("🚇 Chennai Metro Visualizer")

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    start = st.selectbox("📍 Start", all_stations)
with col2:
    end = st.selectbox("🏁 End", all_stations, index=5)

path, msg = get_full_route(start, end)
stops = len(path) - 1
km = stops * 1.5
if km <= 2: fare = 10
elif km <= 5: fare = 20
elif km <= 12: fare = 30
elif km <= 21: fare = 40
else: fare = 50

with col3:
    st.markdown(f"### 🎫 Fare: ₹{fare}")
    st.markdown(f"**🛑 Stops:** {stops}")
    st.info(f"Route: {msg}")

# --- 4. MAP VISUALIZATION (VISUAL UPGRADE) ---
if len(path) > 0:
    route_coords = []
    for s in path:
        if s in station_coords:
            lat, lon = station_coords[s]
            route_coords.append([lon, lat])

    # 1. Path Layer (Thinner, Gold/Orange Color)
    layer_path = pdk.Layer(
        "PathLayer",
        data=[{"path": route_coords}],
        get_path="path",
        get_color=[255, 165, 0], # <-- CHANGED TO GOLD/ORANGE
        get_width=250,           # <-- CHANGED THICKNESS (was 600)
        width_min_pixels=3,
        pickable=True
    )

    # 2. Scatter Layer (Stations remain red)
    layer_scatter = pdk.Layer(
        "ScatterplotLayer",
        data=[{"position": [lon, lat], "name": s} for s, [lat, lon] in station_coords.items() if s in path],
        get_position="position",
        get_color=[255, 50, 50], # Bright Red
        get_radius=250, 
        pickable=True,
    )

    # 3. View State (2D Top-Down)
    view_state = pdk.ViewState(
        latitude=route_coords[len(route_coords)//2][1],
        longitude=route_coords[len(route_coords)//2][0],
        zoom=12, 
        pitch=0,
        bearing=0
    )

    # 4. RENDER MAP
    st.pydeck_chart(pdk.Deck(
        map_style=None, 
        initial_view_state=view_state,
        layers=[layer_path, layer_scatter],
        tooltip={"text": "{name}"}
    ))
