import pandas as pd
import streamlit as st
import plotly.express as px
import json

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('ict_in_education.csv')
    return df

# Load GeoJSON for Nepal's districts
@st.cache_data
def load_geojson():
    with open('nepal-districts-new-reduced.json') as f:
        geojson_data = json.load(f)
    return geojson_data

# Main function to render the ICT in Education dashboard
def main():
    st.title("ICT in Education - Schools Visualization")

    # Load data
    df = load_data()
    geojson_data = load_geojson()

    # Data preprocessing: Drop missing latitudes and longitudes
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Sidebar filters
    st.sidebar.header("Filters")
    province_filter = st.sidebar.multiselect(
        "Select Province",
        options=df["Province"].unique(),
        default=df["Province"].unique()
    )
    
    district_filter = st.sidebar.multiselect(
        "Select District",
        options=df["DIST_EN"].unique(),
        default=df["DIST_EN"].unique()
    )

    program_filter = st.sidebar.multiselect(
        "Select Program",
        options=df["Program"].unique(),
        default=df["Program"].unique()
    )

    # Apply filters
    filtered_df = df[
        (df["Province"].isin(province_filter)) &
        (df["DIST_EN"].isin(district_filter)) &
        (df["Program"].isin(program_filter))
    ]

    # Plot the schools on a map using Plotly
    st.subheader(f"Total Schools: {len(filtered_df)}")

    fig = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="School",
        hover_data=["Address", "Program", "Province", "DIST_EN"],
        color="Province",
        zoom=6,
        height=600
    )

    # Update mapbox style
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # Display the map
    st.plotly_chart(fig)

    # Display filtered data
    st.subheader("Filtered Schools Data")
    st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
