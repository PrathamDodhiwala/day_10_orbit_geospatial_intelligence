
# ORBIT — Geospatial Intelligence & Mobility Explorer

Day 10 of the 60-Day End-of-Year Project Marathon.

ORBIT is an interactive geospatial analytics application built with
Python, Streamlit, Pandas, NumPy and Plotly.

It transforms geographic records into interactive maps, hotspot
summaries, movement analysis and temporal insights.

## Features

- Synthetic geographic demo dataset.
- CSV upload.
- Coordinate validation.
- Interactive geographic activity map.
- Category and zone filtering.
- Grid-based hotspot detection.
- Origin-to-destination movement visualisation.
- Haversine distance calculation.
- Hourly and weekday activity analysis.
- Zone-category activity matrix.
- Filtered event export.
- Hotspot summary export.
- Dataset quality summary.

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly

## CSV Input Format

Required columns:

| timestamp | latitude | longitude | category |
|---|---:|---:|---|
| 2026-11-10 10:30:00 | 19.0760 | 72.8777 | Transit |
| 2026-11-10 11:00:00 | 19.0176 | 72.8562 | Delivery |

Optional columns:

- event_id
- zone
- magnitude
- origin_latitude
- origin_longitude
- destination_latitude
- destination_longitude

The movement analysis page requires all four origin and destination
coordinate columns.

## Installation — Windows / PowerShell

Create a virtual environment:

    py -3.10 -m venv .venv

Activate it:

    .\.venv\Scripts\Activate.ps1

If PowerShell blocks activation:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\.venv\Scripts\Activate.ps1

Install packages:

    python -m pip install --upgrade pip --timeout 600 --retries 10

    python -m pip install -r requirements.txt --no-cache-dir --timeout 600 --retries 10

Run:

    streamlit run app.py

## Getting Started

1. Launch ORBIT.
2. Select Synthetic demo.
3. Explore Geo Overview.
4. Open Hotspot Atlas.
5. Inspect Movement Routes.
6. Compare activity in Time & Regions.
7. Export the results.

## Analytical Methods

- Geographic coordinate validation.
- Haversine great-circle distance.
- Rounded-coordinate grid aggregation.
- Category and zone aggregation.
- Temporal grouping by hour and weekday.

## Important Limitations

The demo records are synthetic and are not real mobility observations.

Hotspot detection uses rounded coordinate grid cells. It is not
DBSCAN, kernel density estimation, or a statistically validated
clustering method.

Haversine distance is straight-line distance, not road distance.

The map is an analytical visualisation, not a live navigation system.
