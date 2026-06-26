import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

DB_PATH = "weather_data.duckdb"

st.set_page_config(
    page_title="Weather ELT Pipeline",
    page_icon="⛅",
    layout="wide"
)

st.title("⛅ German Cities Weather Dashboard")
st.caption("Pipeline: Open Meteo API → Prefect → DuckDB → dbt → Streamlit")

@st.cache_data
def load_data():
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute("SELECT * FROM mart_weather_summary").df()
    con.close()
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
cities = sorted(df["city"].unique())
selected_cities = st.sidebar.multiselect("Select cities", cities, default=cities)
date_range = st.sidebar.date_input(
    "Date range",
    [df["date"].min(), df["date"].max()]
)

# Filter data
filtered = df[
    (df["city"].isin(selected_cities)) &
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1]))
]

# KPI metrics
st.subheader("Summary")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Max Temp", f"{filtered['temp_max_c'].max():.1f}°C")
col2.metric("Min Temp", f"{filtered['temp_min_c'].min():.1f}°C")
col3.metric("Avg Temp", f"{filtered['temp_avg_c'].mean():.1f}°C")
col4.metric("Total Rain", f"{filtered['precipitation_mm'].sum():.1f}mm")
col5.metric("Max Wind", f"{filtered['windspeed_max_kmh'].max():.1f}km/h")

st.divider()

# Row 1 - Temperature over time
st.subheader("Temperature over time")
fig1 = px.line(
    filtered, x="date", y="temp_avg_c",
    color="city",
    labels={"temp_avg_c": "Avg Temp (°C)", "date": "Date"},
    markers=True
)
st.plotly_chart(fig1, use_container_width=True)

# Row 2 - Two charts side by side
col1, col2 = st.columns(2)

with col1:
    st.subheader("7-day rolling average")
    fig2 = px.line(
        filtered, x="date", y="temp_7day_rolling_avg",
        color="city",
        labels={"temp_7day_rolling_avg": "Rolling Avg (°C)"}
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Daily precipitation")
    fig3 = px.bar(
        filtered, x="date", y="precipitation_mm",
        color="city", barmode="group",
        labels={"precipitation_mm": "Precipitation (mm)"}
    )
    st.plotly_chart(fig3, use_container_width=True)

# Row 3 - Two charts side by side
col1, col2 = st.columns(2)

with col1:
    st.subheader("Temperature categories")
    cat_counts = filtered.groupby(
        ["city", "temp_category"]
    ).size().reset_index(name="days")
    fig4 = px.bar(
        cat_counts, x="city", y="days",
        color="temp_category", barmode="stack",
        labels={"days": "Number of days"},
        color_discrete_map={
            "extreme_heat": "#d73027",
            "warm":         "#fc8d59",
            "mild":         "#fee090",
            "cool":         "#91bfdb",
            "cold":         "#4575b4"
        }
    )
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.subheader("Wind speed by city")
    fig5 = px.box(
        filtered, x="city", y="windspeed_max_kmh",
        color="city",
        labels={"windspeed_max_kmh": "Max Wind Speed (km/h)"}
    )
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

# Raw data table
with st.expander("Raw data"):
    st.dataframe(
        filtered.sort_values(["city", "date"]),
        use_container_width=True
    )