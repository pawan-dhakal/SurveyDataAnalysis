# streamlit_app.py
import streamlit as st
import survey_analysis as sa
import pandas as pd
import plotly.express as px

# -------------------------
# PAGE CONFIGURATION
# -------------------------
st.set_page_config(
    page_title="School Survey Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# LOAD DATA (CACHED)
# -------------------------
@st.cache_data
def load_data_cached(filepath):
    return sa.load_data(filepath)


# -------------------------
# SIDEBAR DATA SOURCE SELECTION
# -------------------------
st.sidebar.header("📁 Data Source Selection")

# Define available CSV files
available_datasets = [
    'combined_cleaned_survey_records_Dec2025_withEAST.csv',
    'combined_LLEST_first_survey_records.csv',
    'cleaned_surkhet_dailekh_combined_east_all_Dec2025.csv'
]

# Create selectbox for dataset selection
selected_dataset = st.sidebar.selectbox(
    "Select Dataset:",
    available_datasets,
    index=0,  # Default to first dataset
    help="Choose which dataset to analyze"
)

# Load the selected dataset
df = load_data_cached(selected_dataset)

# Display dataset info
st.sidebar.info(f"📊 **Current Dataset:**\n\n{selected_dataset}")

st.sidebar.markdown("---")

# -------------------------
# SIDEBAR SCHOOL SELECTION
# -------------------------
st.sidebar.header("🏫 School Selection")

# Get list of schools and add 'All' option
schools = sorted(df['school'].unique().tolist())
options = ["All"] + schools

# School selection with checkboxes
selected_schools = []
all_schools = st.sidebar.checkbox("All Schools", value=True)

if all_schools:
    selected_schools = schools
else:
    selected_schools = [
        school for school in schools
        if st.sidebar.checkbox(school, value=False)
    ]

# -------------------------
# DATA FILTERING LOGIC
# -------------------------
def apply_filters(df):
    if selected_schools:
        return df[df['school'].isin(selected_schools)]
    return df


df_filtered = apply_filters(df)

# -------------------------
# TABS STRUCTURE
# -------------------------
tab_overview, tab_numeracy, tab_reading = st.tabs([
    "📊 Overview",
    "🧮 Numeracy Analysis",
    "📖 Reading Analysis"
])

# -------------------------
# OVERVIEW TAB: Enhanced visual summary using filtered data
# -------------------------
with tab_overview:
    st.header("📊 Survey Data Overview")

    # Generate all summary figures based on the complete dataset (df)
    overview_results = sa.plot_overview_summary(
        df, 
        sa.numeracy_ids, 
        sa.long_eng_reading_ids, 
        sa.long_nep_reading_ids
    )

    # Display Summary Metrics in two columns with Unicode icons
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Total Students Surveyed", overview_results["total_students"])
    with col2:
        st.metric("🏫 Total Schools Represented", overview_results["total_schools"])

    st.markdown("---")

    # Display Overall Average Performance Summary
    st.subheader("⭐ Average Performance Summary")
    st.plotly_chart(overview_results["fig_performance"], use_container_width=True, key="overview_performance")

    st.markdown("---")

    # Display School Performance Comparison (Competency by School)
    st.subheader("🏆 Competency Comparison Across Schools")
    st.plotly_chart(overview_results["fig_summary"], use_container_width=True, key="overview_summary")

    st.markdown("---")

    # Display Demographics: Gender and Grade
    st.subheader("👥 Population Breakdown")
    row1_col1, row1_col2 = st.columns([2, 3])
    with row1_col1:
        st.plotly_chart(overview_results["fig_gender"], use_container_width=True, key="overview_gender")
    with row1_col2:
        st.plotly_chart(overview_results["fig_grade"], use_container_width=True, key="overview_grade")

    st.markdown("---")

    # Display Age Distribution
    st.subheader("⏳ Age Distribution")
    st.plotly_chart(overview_results["fig_age"], use_container_width=True, key="overview_age")
    
# -------------------------
# NUMERACY TAB
# -------------------------
with tab_numeracy:
    st.header("🧮 Numeracy Skills Analysis")

    numeracy_analysis = sa.numeracy_analysis(df_filtered, sa.numeracy_ids)
    plots = sa.plot_numeracy_results(numeracy_analysis)

    # Display Summary Metrics in two columns with Unicode icons
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Total Students Surveyed", len(df_filtered))
    with col2:
        schools = sorted(df_filtered['school'].unique())
        if len(schools) > 1:
            school_text = "<br>".join(schools)
        else:
            school_text = schools[0]
        st.markdown(f"**🏫 Selected Schools:**<br>{school_text}", unsafe_allow_html=True)

    st.subheader("Task Completion Rates")
    st.plotly_chart(plots['fig_overall'], use_container_width=True, key="num_overall")

    st.subheader("Performance by Gender")
    st.plotly_chart(plots['fig_gender'], use_container_width=True, key="num_gender")

    if plots['fig_age']:
        st.subheader("Age-wise Progression")
        st.plotly_chart(plots['fig_age'], use_container_width=True, key="num_age")

    if plots['fig_grade']:
        st.subheader("Grade-level Performance")
        st.plotly_chart(plots['fig_grade'], use_container_width=True, key="num_grade")

# -------------------------
# READING TAB: Separate Sub-Tabs for English & Nepali
# -------------------------
with tab_reading:
    st.header("📖 Reading Proficiency Analysis")

    # Display Summary Metrics in two columns with Unicode icons
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Total Students Surveyed", len(df_filtered))
    with col2:
        schools = sorted(df_filtered['school'].unique())
        if len(schools) > 1:
            school_text = "<br>".join(schools)
        else:
            school_text = schools[0]
        st.markdown(f"**🏫 Selected Schools:**<br>{school_text}", unsafe_allow_html=True)

    # Create sub-tabs for English and Nepali reading analysis
    tab_eng, tab_nep = st.tabs([
        "📖 English Reading Analysis",
        "📖 Nepali Reading Analysis"
    ])

    # -------------------------
    # English Reading Analysis
    # -------------------------
    with tab_eng:
        st.subheader("English Reading Analysis")
        
        # Run reading analysis for English reading tasks
        eng_res = sa.reading_analysis(df_filtered, sa.long_eng_reading_ids, lang="English")
        
        # Generate improved reading plots using the new function
        reading_plots_eng = sa.plot_reading_results(eng_res, df_filtered)
        
        # Display Overall Reading Performance
        st.plotly_chart(reading_plots_eng["fig_overall"], use_container_width=True, key="eng_overall")
        
        # Display Gender Breakdown
        st.plotly_chart(reading_plots_eng["fig_gender"], use_container_width=True, key="eng_gender")
        
        # Display Age Breakdown (if available)
        if reading_plots_eng["fig_age"]:
            st.plotly_chart(reading_plots_eng["fig_age"], use_container_width=True, key="eng_age")
        
        # Display Grade Breakdown (if available)
        if reading_plots_eng["fig_grade"]:
            st.plotly_chart(reading_plots_eng["fig_grade"], use_container_width=True, key="eng_grade")

    # -------------------------
    # Nepali Reading Analysis
    # -------------------------
    with tab_nep:
        st.subheader("Nepali Reading Analysis")
        
        # Run reading analysis for Nepali reading tasks
        nep_res = sa.reading_analysis(df_filtered, sa.long_nep_reading_ids, lang="Nepali")
        
        # Generate improved reading plots for Nepali using the new function
        reading_plots_nep = sa.plot_reading_results(nep_res, df_filtered)
        
        # Display Overall Reading Performance
        st.plotly_chart(reading_plots_nep["fig_overall"], use_container_width=True, key="nep_overall")
        
        # Display Gender Breakdown
        st.plotly_chart(reading_plots_nep["fig_gender"], use_container_width=True, key="nep_gender")
        
        # Display Age Breakdown (if available)
        if reading_plots_nep["fig_age"]:
            st.plotly_chart(reading_plots_nep["fig_age"], use_container_width=True, key="nep_age")
        
        # Display Grade Breakdown (if available)
        if reading_plots_nep["fig_grade"]:
            st.plotly_chart(reading_plots_nep["fig_grade"], use_container_width=True, key="nep_grade")