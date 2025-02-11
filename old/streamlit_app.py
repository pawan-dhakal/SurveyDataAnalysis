import streamlit as st
import survey_analysis as sa
import pandas as pd

# -------------------------
# PAGE CONFIGURATION
# -------------------------
st.set_page_config(
    page_title="Survey Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# LOAD DATA
# -------------------------
data_path = 'combined_cleaned_survey_records.csv'
df = sa.load_data(data_path)

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.header("Filter Options")

# School Filter (using "All" for no filtering)
school_options = sorted(df['school'].dropna().unique().tolist())
school_options.insert(0, "All")
selected_school = st.sidebar.selectbox("Select School", options=school_options)

# Grade Filter (multi-select)
grade_options = sorted(df['grade'].dropna().unique().tolist())
selected_grades = st.sidebar.multiselect("Select Grades", options=grade_options, default=grade_options)

# Gender Filter (multi-select)
gender_options = sorted(df['studentGender'].dropna().unique().tolist())
selected_genders = st.sidebar.multiselect("Select Gender", options=gender_options, default=gender_options)

# Age Range Filter (using slider)
age_min = int(df['studentAge'].min())
age_max = int(df['studentAge'].max())
selected_age_range = st.sidebar.slider("Select Age Range", age_min, age_max, (age_min, age_max))

st.sidebar.markdown("---")
st.sidebar.info("All analyses will use the filtered data below.")

# -------------------------
# APPLY FILTERS TO THE DATA
# -------------------------
df_filtered = df.copy()

# Filter by school (if not "All")
if selected_school != "All":
    df_filtered = df_filtered[df_filtered['school'] == selected_school]

# Filter by grade
if selected_grades:
    df_filtered = df_filtered[df_filtered['grade'].isin(selected_grades)]

# Filter by gender
if selected_genders:
    df_filtered = df_filtered[df_filtered['studentGender'].isin(selected_genders)]

# Filter by age range
df_filtered = df_filtered[(df_filtered['studentAge'] >= selected_age_range[0]) & 
                          (df_filtered['studentAge'] <= selected_age_range[1])]

# -------------------------
# TAB LAYOUT FOR ORGANIZED DISPLAY
# -------------------------
tabs = st.tabs(["Overview", "Numeracy Analysis", "Reading Analysis", "Raw Data"])

# -------------------------
# TAB 1: OVERVIEW
# -------------------------
with tabs[0]:
    st.header("Survey Data Overview")
    st.markdown(f"**Total Records:** {df_filtered.shape[0]}")
    st.dataframe(df_filtered.head(10), use_container_width=True)
    st.markdown("_Use the sidebar filters to refine the data shown in the analysis tabs._")

# -------------------------
# TAB 2: NUMERACY ANALYSIS
# -------------------------
with tabs[1]:
    st.header("Numeracy Analysis")
    
    # Define the numeracy question IDs (as in the original script)
    numeracy_ids = [
        "FL23_cleaned1", "FL23_cleaned2", "FL23_cleaned3", "FL23_cleaned4", "FL23_cleaned5", 
        "FL23_cleaned6", "FL24_cleaned1", "FL24_cleaned2", "FL24_cleaned3", "FL24_cleaned4", "FL24_cleaned5", 
        "FL25_cleaned1", "FL25_cleaned2", "FL25_cleaned3", "FL25_cleaned4", "FL25_cleaned5", 
        "FL26", "FL26C", "FL27_cleaned1", "FL27_cleaned2", "FL27_cleaned3", "FL27_cleaned4"
    ]
    
    # Run numeracy analysis on the filtered data.
    # (Pass school=None because filtering is already applied above.)
    if df_filtered.empty:
        st.error("No records match the current filters. Please adjust your filter selections.")
    else:
        numeracy_results = sa.numeracy_analysis(df_filtered, numeracy_ids, school=None, printText=False)
        
        # Display formatted results using markdown.
        st.markdown(sa.get_formatted_numeracy_results(numeracy_results))
        
        # Plot overall and gender breakdown charts.
        st.plotly_chart(sa.plot_numeracy_results(numeracy_results)["fig_overall"], use_container_width=True)
        st.plotly_chart(sa.plot_numeracy_results(numeracy_results)["fig_gender"], use_container_width=True)
        
        # Optionally show age and grade plots if available.
        num_figs = sa.plot_numeracy_results(numeracy_results)
        if num_figs["fig_age"] is not None:
            st.plotly_chart(num_figs["fig_age"], use_container_width=True)
        if num_figs["fig_grade"] is not None:
            st.plotly_chart(num_figs["fig_grade"], use_container_width=True)

# -------------------------
# TAB 3: READING ANALYSIS
# -------------------------
with tabs[2]:
    st.header("Reading Analysis")
    
    # Language selection for reading analysis
    language_options = ["English", "Nepali"]
    selected_language = st.selectbox("Select Language for Reading Analysis", options=language_options, index=0)
    
    # Depending on language, set total word count and question IDs.
    if selected_language == "English":
        total_long_words = 61  # e.g., total words for the English long reading task 
        total_short_words = 14
        eng_reading_ids = ['FL13_cleaned', 'FL15', 'FL17', 'FL19_cleaned', 'FL21B_cleaned1', 
                             'FL21B_cleaned2', 'FL21B_cleaned3', 'FL21B_cleaned4', 'FL21B_cleaned5']
        # For example, use indices 3-8 for the long reading task.
        long_reading_ids = [eng_reading_ids[i] for i in [3, 4, 5, 6, 7, 8]]
        # short_reading_ids could be used elsewhere if needed.
        short_reading_ids = [eng_reading_ids[i] for i in [0, 1, 2]]
        reading_ids = long_reading_ids
    elif selected_language == "Nepali":
        total_long_words = 48  # e.g., total words for the Nepali long reading task
        total_short_words = 16
        nep_reading_ids = ["FL21G_cleaned", "FL21I", "FL21K", "FL21O_cleaned", 
                           "FL22_cleaned1", "FL22_cleaned2", "FL22_cleaned3", "FL22_cleaned4", "FL22_cleaned5"]
        long_reading_ids = [nep_reading_ids[i] for i in [3, 4, 5, 6, 7, 8]]
        short_reading_ids = [nep_reading_ids[i] for i in [0, 1, 2]]
        reading_ids = long_reading_ids

    if df_filtered.empty:
        st.error("No records match the current filters. Please adjust your filter selections.")
    else:
        # Run reading analysis on the filtered data.
        reading_results = sa.reading_analysis(df_filtered, reading_ids, total_long_words, lang=selected_language, school=None, printText=False)
    
        # Display formatted reading results.
        st.markdown(sa.get_formatted_reading_results(reading_results, selected_language))
    
        # Plot reading analysis chart.
        reading_fig = sa.plot_reading_results(reading_results, selected_language, selected_school)
        st.plotly_chart(reading_fig, use_container_width=True)

# -------------------------
# TAB 4: RAW DATA
# -------------------------
with tabs[3]:
    st.header("Raw Data")
    st.dataframe(df_filtered, use_container_width=True)
