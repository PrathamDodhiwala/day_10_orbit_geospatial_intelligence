
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from datetime import datetime, timedelta

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="ORBIT | Geospatial Intelligence",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# VISUAL IDENTITY — CARTOGRAPHY STUDIO
# ==========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --paper: #F4F1E9;
    --white: #FFFEFA;
    --ink: #172B3A;
    --muted: #75838A;
    --line: #DDDCD2;
    --orange: #E66B3D;
    --blue: #2F6F8F;
    --green: #53866B;
}
.stApp {
    background: var(--paper);
    color: var(--ink);
    font-family: 'Manrope', sans-serif;
}
[data-testid="stSidebar"] {
    background: #EAE7DD;
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] * {
    color: var(--ink);
}
.block-container {
    max-width: 1550px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3, p, label {
    color: var(--ink);
}
.eyebrow {
    color: var(--orange);
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.hero {
    font-size: clamp(38px, 5vw, 62px);
    font-weight: 800;
    letter-spacing: -3px;
    line-height: 1.02;
    margin-top: 8px;
}
.subtitle {
    color: var(--muted);
    max-width: 780px;
    font-size: 14px;
    line-height: 1.8;
    margin-top: 12px;
}
.metric {
    background: var(--white);
    border: 1px solid var(--line);
    border-radius: 13px;
    padding: 17px;
    min-height: 108px;
}
.metric-label {
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.metric-value {
    color: var(--ink);
    font-size: 29px;
    font-weight: 800;
    letter-spacing: -1.5px;
    margin-top: 8px;
}
.metric-note {
    color: var(--muted);
    font-size: 11px;
    margin-top: 2px;
}
.section-heading {
    font-size: 21px;
    font-weight: 800;
    letter-spacing: -0.8px;
    margin-top: 20px;
    margin-bottom: 8px;
}
.panel {
    background: var(--white);
    border: 1px solid var(--line);
    border-radius: 13px;
    padding: 18px;
}
.mono {
    font-family: 'DM Mono', monospace;
    color: var(--muted);
    font-size: 10px;
}
.stButton > button, .stDownloadButton > button {
    background: var(--ink);
    color: white;
    border: 0;
    border-radius: 7px;
    min-height: 40px;
    font-weight: 700;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: var(--orange);
    color: white;
    border: 0;
}
div[data-testid="stMetric"] {
    background: var(--white);
    border: 1px solid var(--line);
    padding: 12px;
    border-radius: 10px;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 9px;
}
hr {
    border-color: var(--line);
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# CONSTANTS
# ==========================================================
INK = "#172B3A"
ORANGE = "#E66B3D"
BLUE = "#2F6F8F"
GREEN = "#53866B"
MUTED = "#75838A"
PAPER = "#F4F1E9"
WHITE = "#FFFEFA"

CATEGORIES = [
    "Transit",
    "Delivery",
    "Service",
    "Public Event",
    "Incident"
]

# ==========================================================
# SYNTHETIC GEOGRAPHIC DATA
# Demo area: fictionalised urban activity around Mumbai.
# ==========================================================
def generate_demo_data(n=1200, seed=42):
    rng = np.random.default_rng(seed)

    # Approximate demo centres around an urban area.
    centres = [
        (19.0760, 72.8777, "Central"),
        (19.0176, 72.8562, "South"),
        (19.1136, 72.8697, "North"),
        (19.0596, 72.8295, "West"),
        (19.2183, 72.9781, "East")
    ]

    weights = [0.30, 0.16, 0.20, 0.18, 0.16]
    chosen = rng.choice(len(centres), size=n, p=weights)

    latitudes = []
    longitudes = []
    zones = []

    for index in chosen:
        lat, lon, zone = centres[index]
        latitudes.append(lat + rng.normal(0, 0.012))
        longitudes.append(lon + rng.normal(0, 0.014))
        zones.append(zone)

    now = datetime.now()
    timestamps = [
        now - timedelta(
            minutes=int(rng.integers(0, 7 * 24 * 60))
        )
        for _ in range(n)
    ]

    categories = rng.choice(
        CATEGORIES,
        size=n,
        p=[0.35, 0.27, 0.17, 0.13, 0.08]
    )

    magnitude = np.clip(
        rng.gamma(shape=2.2, scale=18, size=n),
        1,
        150
    ).round(1)

    origin_lat = []
    origin_lon = []
    destination_lat = []
    destination_lon = []

    for lat, lon in zip(latitudes, longitudes):
        origin_lat.append(lat + rng.normal(0, 0.018))
        origin_lon.append(lon + rng.normal(0, 0.020))
        destination_lat.append(lat)
        destination_lon.append(lon)

    return pd.DataFrame({
        "event_id": [f"ORB-{i+1:05d}" for i in range(n)],
        "timestamp": timestamps,
        "latitude": latitudes,
        "longitude": longitudes,
        "category": categories,
        "zone": zones,
        "magnitude": magnitude,
        "origin_latitude": origin_lat,
        "origin_longitude": origin_lon,
        "destination_latitude": destination_lat,
        "destination_longitude": destination_lon
    })


# ==========================================================
# GEOSPATIAL FUNCTIONS
# ==========================================================
def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two coordinates.
    Inputs may be NumPy arrays or scalar values.
    """
    earth_radius = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return 2 * earth_radius * np.arcsin(
        np.sqrt(np.clip(a, 0, 1))
    )


def prepare_data(df):
    required = ["timestamp", "latitude", "longitude", "category"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    data = df.copy()

    data["timestamp"] = pd.to_datetime(
        data["timestamp"], errors="coerce"
    )
    data["latitude"] = pd.to_numeric(
        data["latitude"], errors="coerce"
    )
    data["longitude"] = pd.to_numeric(
        data["longitude"], errors="coerce"
    )

    data = data.dropna(
        subset=["timestamp", "latitude", "longitude"]
    )

    # Valid geographic coordinate ranges.
    data = data[
        data["latitude"].between(-90, 90)
        & data["longitude"].between(-180, 180)
    ].copy()

    if data.empty:
        raise ValueError(
            "No valid records remain. Check timestamps and coordinates."
        )

    data["category"] = (
        data["category"].fillna("Unclassified").astype(str)
    )

    if "zone" not in data.columns:
        data["zone"] = "Unassigned"

    if "magnitude" not in data.columns:
        data["magnitude"] = 1.0

    data["magnitude"] = pd.to_numeric(
        data["magnitude"], errors="coerce"
    ).fillna(1.0).clip(lower=0)

    if "event_id" not in data.columns:
        data["event_id"] = [
            f"UPLOAD-{i+1:05d}" for i in range(len(data))
        ]

    route_columns = [
        "origin_latitude",
        "origin_longitude",
        "destination_latitude",
        "destination_longitude"
    ]

    for col in route_columns:
        if col not in data.columns:
            data[col] = np.nan
        else:
            data[col] = pd.to_numeric(
                data[col], errors="coerce"
            )

    route_valid = (
        data[route_columns].notna().all(axis=1)
        & data["origin_latitude"].between(-90, 90)
        & data["destination_latitude"].between(-90, 90)
        & data["origin_longitude"].between(-180, 180)
        & data["destination_longitude"].between(-180, 180)
    )

    data["route_distance_km"] = np.nan

    data.loc[route_valid, "route_distance_km"] = haversine_km(
        data.loc[route_valid, "origin_latitude"],
        data.loc[route_valid, "origin_longitude"],
        data.loc[route_valid, "destination_latitude"],
        data.loc[route_valid, "destination_longitude"]
    )

    data["hour"] = data["timestamp"].dt.hour
    data["day_name"] = data["timestamp"].dt.day_name()

    return data.sort_values("timestamp").reset_index(drop=True)


def make_hotspots(data, precision=2):
    """
    Group coordinates into rounded geographic grid cells.
    This is a simple grid-based hotspot method, not DBSCAN.
    """
    temp = data.copy()
    temp["grid_lat"] = temp["latitude"].round(precision)
    temp["grid_lon"] = temp["longitude"].round(precision)

    hotspots = (
        temp.groupby(["grid_lat", "grid_lon"])
        .agg(
            event_count=("event_id", "count"),
            average_magnitude=("magnitude", "mean"),
            categories=("category", "nunique")
        )
        .reset_index()
        .sort_values("event_count", ascending=False)
    )

    return hotspots


def chart_layout(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(
            family="Manrope",
            color=INK
        ),
        margin=dict(l=15, r=15, t=45, b=15),
        xaxis=dict(
            gridcolor="#E9E6DD",
            zerolinecolor="#E9E6DD"
        ),
        yaxis=dict(
            gridcolor="#E9E6DD",
            zerolinecolor="#E9E6DD"
        )
    )
    return fig


def page_header(kicker, title, description):
    st.markdown(
        f"<div class='eyebrow'>{kicker}</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div class='hero'>{title}</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div class='subtitle'>{description}</div>",
        unsafe_allow_html=True
    )
    st.write("")


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def make_map(data, show_routes=False, max_routes=100):
    fig = go.Figure()

    if show_routes:
        route_data = data.dropna(
            subset=[
                "origin_latitude",
                "origin_longitude",
                "destination_latitude",
                "destination_longitude"
            ]
        ).head(max_routes)

        for _, row in route_data.iterrows():
            fig.add_trace(go.Scattergeo(
                lon=[
                    row["origin_longitude"],
                    row["destination_longitude"]
                ],
                lat=[
                    row["origin_latitude"],
                    row["destination_latitude"]
                ],
                mode="lines",
                line=dict(
                    width=0.8,
                    color="rgba(47,111,143,0.25)"
                ),
                hoverinfo="skip",
                showlegend=False
            ))

    category_colors = {
        "Transit": BLUE,
        "Delivery": ORANGE,
        "Service": GREEN,
        "Public Event": "#9476B8",
        "Incident": "#C84C4C"
    }

    for category in sorted(data["category"].unique()):
        subset = data[data["category"] == category]

        fig.add_trace(go.Scattergeo(
            lon=subset["longitude"],
            lat=subset["latitude"],
            text=(
                "Event: " + subset["event_id"].astype(str)
                + "<br>Category: " + subset["category"].astype(str)
                + "<br>Zone: " + subset["zone"].astype(str)
                + "<br>Magnitude: " + subset["magnitude"].round(1).astype(str)
                + "<br>Time: " + subset["timestamp"].astype(str)
            ),
            mode="markers",
            name=category,
            marker=dict(
                size=7,
                color=category_colors.get(category, MUTED),
                opacity=0.75,
                line=dict(width=0.5, color=WHITE)
            ),
            hovertemplate="%{text}<extra></extra>"
        ))

    fig.update_layout(
        height=590,
        paper_bgcolor=WHITE,
        geo=dict(
            scope="asia",
            projection_type="mercator",
            showland=True,
            landcolor="#E8E5DA",
            showocean=True,
            oceancolor="#DCEAF0",
            showlakes=True,
            lakecolor="#DCEAF0",
            showcountries=True,
            countrycolor="#C9C9BD",
            showcoastlines=True,
            coastlinecolor="#AAB6B4",
            showframe=False,
            lataxis=dict(showgrid=True, gridcolor="#D9E1DE"),
            lonaxis=dict(showgrid=True, gridcolor="#D9E1DE")
        ),
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            x=0.02
        )
    )

    return fig


# ==========================================================
# SIDEBAR — SOURCE
# ==========================================================
st.sidebar.markdown("## ◎ ORBIT")
st.sidebar.markdown(
    "<div class='mono'>GEOSPATIAL INTELLIGENCE / DAY 10</div>",
    unsafe_allow_html=True
)
st.sidebar.divider()

source = st.sidebar.radio(
    "DATA SOURCE",
    ["Synthetic demo", "Upload CSV"]
)

if source == "Synthetic demo":
    raw = generate_demo_data()
    source_label = "ORBIT synthetic urban activity"
else:
    upload = st.sidebar.file_uploader(
        "Upload geographic CSV",
        type=["csv"]
    )

    if upload is None:
        page_header(
            "DATA INPUT / 001",
            "Bring your coordinates.",
            "Upload a CSV containing timestamp, latitude, longitude "
            "and category columns to explore your geographic data."
        )
        st.info(
            "No dataset? Switch to Synthetic demo to explore ORBIT."
        )
        st.stop()

    try:
        raw = pd.read_csv(upload)
        source_label = upload.name
    except Exception as error:
        st.error(f"Could not read CSV: {error}")
        st.stop()

try:
    data = prepare_data(raw)
except Exception as error:
    st.error(f"Could not prepare geographic data: {error}")
    st.stop()

# ==========================================================
# SIDEBAR — FILTERS
# ==========================================================
st.sidebar.divider()
st.sidebar.markdown("### MAP FILTERS")

categories = sorted(data["category"].unique())
selected_categories = st.sidebar.multiselect(
    "Activity categories",
    categories,
    default=categories
)

zones = sorted(data["zone"].astype(str).unique())
selected_zones = st.sidebar.multiselect(
    "Zones",
    zones,
    default=zones
)

min_date = data["timestamp"].min().date()
max_date = data["timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

filtered = data[
    data["category"].isin(selected_categories)
    & data["zone"].astype(str).isin(selected_zones)
    & (
        data["timestamp"].dt.date >= start_date
    )
    & (
        data["timestamp"].dt.date <= end_date
    )
].copy()

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ==========================================================
# NAVIGATION
# ==========================================================
st.sidebar.divider()
page = st.sidebar.radio(
    "EXPLORER",
    [
        "Geo Overview",
        "Hotspot Atlas",
        "Movement Routes",
        "Time & Regions",
        "Data Export"
    ]
)

st.sidebar.divider()
st.sidebar.markdown(
    f"<div class='mono'>SOURCE: {source_label}<br>"
    f"VALID RECORDS: {len(data):,}<br>"
    f"ORBIT ENGINE / 1.0</div>",
    unsafe_allow_html=True
)

# ==========================================================
# GLOBAL METRICS
# ==========================================================
hotspots = make_hotspots(filtered)
route_values = filtered["route_distance_km"].dropna()

# ==========================================================
# PAGE 1 — GEO OVERVIEW
# ==========================================================
if page == "Geo Overview":
    page_header(
        "SPATIAL OVERVIEW / 001",
        "See the bigger picture.",
        "Explore where activity is happening, how it is distributed, "
        "and which geographic areas deserve a closer look."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Mapped events",
            f"{len(filtered):,}",
            "Records after filtering"
        )
    with c2:
        metric_card(
            "Active zones",
            f"{filtered['zone'].nunique():,}",
            "Distinct named zones"
        )
    with c3:
        metric_card(
            "Hotspot cells",
            f"{len(hotspots):,}",
            "Occupied coordinate grid cells"
        )
    with c4:
        avg_distance = (
            f"{route_values.mean():.2f} km"
            if len(route_values) else "N/A"
        )
        metric_card(
            "Average route",
            avg_distance,
            "Valid origin-to-destination records"
        )

    st.markdown(
        "<div class='section-heading'>Geographic activity map</div>",
        unsafe_allow_html=True
    )

    st.plotly_chart(
        make_map(filtered),
        use_container_width=True
    )

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown(
            "<div class='section-heading'>Activity by category</div>",
            unsafe_allow_html=True
        )

        category_stats = (
            filtered["category"].value_counts()
            .rename_axis("category")
            .reset_index(name="events")
        )

        fig = px.bar(
            category_stats,
            x="category",
            y="events",
            color="category",
            color_discrete_sequence=[
                BLUE, ORANGE, GREEN, "#9476B8", "#C84C4C"
            ]
        )
        fig.update_layout(showlegend=False)
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown(
            "<div class='section-heading'>Activity by zone</div>",
            unsafe_allow_html=True
        )

        zone_stats = (
            filtered["zone"].value_counts()
            .rename_axis("zone")
            .reset_index(name="events")
        )

        fig = px.pie(
            zone_stats,
            names="zone",
            values="events",
            hole=0.58
        )
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# PAGE 2 — HOTSPOT ATLAS
# ==========================================================
elif page == "Hotspot Atlas":
    page_header(
        "SPATIAL DENSITY / 002",
        "Find the hotspots.",
        "Aggregate nearby coordinates into geographic grid cells "
        "to discover where activity is most concentrated."
    )

    precision = st.select_slider(
        "Grid precision",
        options=[1, 2, 3],
        value=2,
        help=(
            "Higher precision creates smaller coordinate cells. "
            "This is coordinate rounding, not a true equal-area grid."
        )
    )

    hotspot_data = make_hotspots(filtered, precision)

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card(
            "Occupied cells",
            f"{len(hotspot_data):,}",
            f"Coordinate precision: {precision}"
        )
    with c2:
        metric_card(
            "Highest cell count",
            f"{int(hotspot_data['event_count'].max()):,}",
            "Events in the busiest cell"
        )
    with c3:
        metric_card(
            "Mean cell activity",
            f"{hotspot_data['event_count'].mean():.1f}",
            "Events per occupied cell"
        )

    st.markdown(
        "<div class='section-heading'>Hotspot map</div>",
        unsafe_allow_html=True
    )

    fig = px.scatter_geo(
        hotspot_data,
        lat="grid_lat",
        lon="grid_lon",
        size="event_count",
        color="event_count",
        hover_data={
            "grid_lat": ":.4f",
            "grid_lon": ":.4f",
            "event_count": True,
            "average_magnitude": ":.1f",
            "categories": True
        },
        color_continuous_scale=["#F5C9A7", ORANGE, "#9D352A"],
        projection="mercator",
        scope="asia",
        size_max=32
    )

    fig.update_geos(
        showland=True,
        landcolor="#E8E5DA",
        showocean=True,
        oceancolor="#DCEAF0",
        showcountries=True,
        countrycolor="#C9C9BD"
    )

    fig.update_layout(
        height=540,
        paper_bgcolor=WHITE,
        margin=dict(l=0, r=0, t=20, b=0),
        coloraxis_colorbar=dict(title="Events")
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='section-heading'>Busiest geographic cells</div>",
        unsafe_allow_html=True
    )

    st.dataframe(
        hotspot_data.head(20).round(3),
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Hotspots are identified through rounded-coordinate aggregation. "
        "They are not statistically validated clusters."
    )

# ==========================================================
# PAGE 3 — MOVEMENT ROUTES
# ==========================================================
elif page == "Movement Routes":
    page_header(
        "MOVEMENT INTELLIGENCE / 003",
        "Trace the movement.",
        "Explore origin-to-destination records, compare trip distances, "
        "and understand how movement varies across activity categories."
    )

    routes = filtered.dropna(
        subset=[
            "origin_latitude",
            "origin_longitude",
            "destination_latitude",
            "destination_longitude"
        ]
    ).copy()

    if routes.empty:
        st.info(
            "No route coordinates are available. Upload the optional "
            "origin and destination columns to use this section."
        )
    else:
        routes = routes[
            routes["route_distance_km"].notna()
        ].copy()

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "Valid routes",
                f"{len(routes):,}",
                "Records with valid endpoints"
            )
        with c2:
            metric_card(
                "Average distance",
                f"{routes['route_distance_km'].mean():.2f} km",
                "Haversine distance"
            )
        with c3:
            metric_card(
                "Longest distance",
                f"{routes['route_distance_km'].max():.2f} km",
                "Great-circle distance"
            )

        st.markdown(
            "<div class='section-heading'>Route network</div>",
            unsafe_allow_html=True
        )

        st.plotly_chart(
            make_map(routes, show_routes=True, max_routes=150),
            use_container_width=True
        )

        left, right = st.columns(2)

        with left:
            fig = px.histogram(
                routes,
                x="route_distance_km",
                nbins=25,
                color_discrete_sequence=[ORANGE]
            )
            chart_layout(fig)
            fig.update_layout(
                title="ROUTE DISTANCE DISTRIBUTION",
                xaxis_title="Distance (km)",
                yaxis_title="Routes"
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            route_category = (
                routes.groupby("category")["route_distance_km"]
                .mean()
                .reset_index()
            )
            fig = px.bar(
                route_category,
                x="category",
                y="route_distance_km",
                color_discrete_sequence=[BLUE]
            )
            chart_layout(fig)
            fig.update_layout(
                title="AVERAGE DISTANCE BY CATEGORY",
                xaxis_title="Category",
                yaxis_title="Distance (km)"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            routes[
                [
                    "event_id",
                    "category",
                    "origin_latitude",
                    "origin_longitude",
                    "destination_latitude",
                    "destination_longitude",
                    "route_distance_km"
                ]
            ].head(100).round(4),
            hide_index=True,
            use_container_width=True
        )

        st.caption(
            "Haversine measures straight-line distance over the Earth's "
            "surface, not actual road or travel distance."
        )

# ==========================================================
# PAGE 4 — TIME & REGIONS
# ==========================================================
elif page == "Time & Regions":
    page_header(
        "TEMPORAL & REGIONAL ANALYSIS / 004",
        "When and where?",
        "Compare activity across hours and days to understand "
        "temporal patterns within geographic areas."
    )

    hourly = (
        filtered.groupby("hour")
        .size()
        .reindex(range(24), fill_value=0)
        .rename("events")
        .reset_index()
    )

    fig = px.bar(
        hourly,
        x="hour",
        y="events",
        color="events",
        color_continuous_scale=["#DCEAF0", BLUE]
    )
    chart_layout(fig)
    fig.update_layout(
        title="ACTIVITY BY HOUR OF DAY",
        xaxis_title="Hour (0–23)",
        yaxis_title="Events",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

    daily = (
        filtered.groupby("day_name")
        .size()
        .rename("events")
        .reset_index()
    )

    order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]
    daily["day_name"] = pd.Categorical(
        daily["day_name"],
        categories=order,
        ordered=True
    )
    daily = daily.sort_values("day_name")

    fig = px.line(
        daily,
        x="day_name",
        y="events",
        markers=True,
        color_discrete_sequence=[ORANGE]
    )
    fig.update_traces(line=dict(width=3))
    chart_layout(fig)
    fig.update_layout(
        title="ACTIVITY BY DAY OF WEEK",
        xaxis_title="Day",
        yaxis_title="Events"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='section-heading'>Zone and category matrix</div>",
        unsafe_allow_html=True
    )

    matrix = pd.pivot_table(
        filtered,
        index="zone",
        columns="category",
        values="event_id",
        aggfunc="count",
        fill_value=0
    )

    fig = px.imshow(
        matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=["#F7E7D9", ORANGE, "#8D3F2B"]
    )
    chart_layout(fig, 400)
    fig.update_layout(
        title="EVENT DISTRIBUTION BY ZONE AND CATEGORY"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# PAGE 5 — DATA EXPORT
# ==========================================================
elif page == "Data Export":
    page_header(
        "DATA DELIVERY / 005",
        "Take the data with you.",
        "Download the filtered geographic records and derived "
        "hotspot summaries for further analysis."
    )

    st.markdown(
        "<div class='section-heading'>Filtered records</div>",
        unsafe_allow_html=True
    )

    st.dataframe(
        filtered.head(20),
        hide_index=True,
        use_container_width=True
    )

    event_csv = filtered.to_csv(index=False).encode("utf-8")
    hotspot_csv = hotspots.to_csv(index=False).encode("utf-8")

    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            "Download filtered events",
            event_csv,
            "orbit_filtered_events.csv",
            "text/csv",
            use_container_width=True
        )

    with c2:
        st.download_button(
            "Download hotspot summary",
            hotspot_csv,
            "orbit_hotspot_summary.csv",
            "text/csv",
            use_container_width=True
        )

    st.markdown(
        "<div class='section-heading'>Dataset quality</div>",
        unsafe_allow_html=True
    )

    quality = pd.DataFrame({
        "Check": [
            "Total input rows",
            "Valid geographic rows",
            "Invalid or missing coordinates removed",
            "Unique categories",
            "Unique zones",
            "Records with route coordinates"
        ],
        "Result": [
            len(raw),
            len(data),
            max(0, len(raw) - len(data)),
            data["category"].nunique(),
            data["zone"].nunique(),
            int(data["route_distance_km"].notna().sum())
        ]
    })

    st.dataframe(
        quality,
        hide_index=True,
        use_container_width=True
    )

# ==========================================================
# FOOTER
# ==========================================================
st.divider()
st.markdown(
    "<div class='mono'>ORBIT GEOSPATIAL INTELLIGENCE · "
    "DAY 10 OF 60 · BUILT WITH PYTHON</div>",
    unsafe_allow_html=True
)
