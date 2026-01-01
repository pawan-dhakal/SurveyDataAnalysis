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
    initial_sidebar_state="expanded",
    
)

# -------------------------
# DATASET CONFIGURATION
# -------------------------
DATASET_CONFIG = {
    "All Records": {
        "file": "combined_cleaned_survey_records_Dec2025_withEAST.csv",
        "description": "Complete dataset including all schools from EAST and LLEST projects",
        "icon": "🌍"
    },
    "EAST School Records": {
        "file": "cleaned_surkhet_dailekh_combined_east_all_Dec2025.csv",
        "description": "Schools from the EAST project (Surkhet & Dailekh regions)",
        "icon": "🏫"
    },
    "LLEST School Records": {
        "file": "combined_LLEST_first_survey_records.csv",
        "description": "Schools from the LLEST project",
        "icon": "📚"
    }
}

# -------------------------
# SCHOOL METADATA (Add location and project info)
# -------------------------
SCHOOL_METADATA = {
    # EAST Project schools
    "Nepal Rastriya Secondary School": {
        "address": "Khajura 8",
        "district": "Surkhet",
        "project": "EAST"
    },
    "Chhabi Basic School": {
        "address": "Kalagaun 4",
        "district": "Surkhet",
        "project": "EAST"
    },
    "Janajagrit Basic School": {
        "address": "Padampur 12",
        "district": "Surkhet",
        "project": "EAST"
    },
    "Janajagriti Basic School - Pyusey": {
        "address": "Narayan 3, Pyusey",
        "district": "Dailekh",
        "project": "EAST"
    },
    "Navadurga Basic School": {
        "address": "Narayan 5, Chhatikot",
        "district": "Dailekh",
        "project": "EAST"
    },
    "Raina Devi Basic School": {
        "address": "Narayan 11, Kanda",
        "district": "Dailekh",
        "project": "EAST"
    },
    # LLEST Project schools
    "Ghami Basic Solar School": {
        "address": "Ghami",
        "district": "Mustang",
        "project": "LLEST"
    },
    "Siddhartha Kula Basic School": {
        "address": "Nilung, Tinje, Dolpo",
        "district": "Dolpo",
        "project": "LLEST"
    },
    "Minnath Adarsha Basic School": {
        "address": "Tangal",
        "district": "Lalitpur",
        "project": "LLEST"
    },
    "Janta Basic School": {
        "address": "Santanagar, Dhangadimai",
        "district": "Dhangadimai",
        "project": "LLEST"
    },
    "Secondary School": {
        "address": "Basabitti 22, Janakpurdham",
        "district": "Janakpurdham",
        "project": "LLEST"
    }
}

# -------------------------
# LOAD DATA (CACHED)
# -------------------------
@st.cache_data
def load_data_cached(filepath):
    """Load raw data from CSV - this is cached for performance"""
    return sa.load_data(filepath)

# -------------------------
# DATA CLEANING HELPERS (NOT CACHED)
# -------------------------
def clean_school_names(df):
    """Clean and standardize school names to avoid duplicates"""
    
    # First, strip whitespace
    df['school'] = df['school'].str.strip()
    
    # Map ALL variations found in the actual data to standard names
    school_name_mapping = {
        # Chhabi Basic School variations
        'Chhabi Basic School- Kalagaun 4 Surkhet': 'Chhabi Basic School',
        'Chhabi Basic School - Kalagaun 4 Surkhet': 'Chhabi Basic School',
        
        # Ghami Basic Solar School variations
        'Ghami Solar Basic School': 'Ghami Basic Solar School',
        
        # Janajagrit Basic School variations (Surkhet)
        'Janajagrit Basic School - Padampur 12 Surkhet': 'Janajagrit Basic School',
        'Janajagrit Basic School- Padampur 12 Surkhet': 'Janajagrit Basic School',
        
        # Janajagriti Basic School variations (Dailekh - note different spelling)
        'JANAJAGRITI BASIC SCHOOL, NARAYAN 3, PYUSEY, DAILEKH': 'Janajagriti Basic School - Pyusey',
        'Janajagriti Basic School, Narayan 3, Pyusey, Dailekh': 'Janajagriti Basic School - Pyusey',
        
        # Janta Basic School variations
        'Janta Aa Vi Santanagar Dhangadimai': 'Janta Basic School',
        'Janta Basic School, Santanagar, Dhangadimai': 'Janta Basic School',
        
        # Minnath Adarsha Basic School variations
        'Minnath Adarsha Basic School LMC': 'Minnath Adarsha Basic School',
        
        # Navadurga Basic School variations
        'NAVADURGA BASIC SCHOOL, NARAYAN 5, CHHATIKOT, DAILEKH': 'Navadurga Basic School',
        
        # Nepal Rastriya Secondary School variations
        'Nepal Rastriya Secondary School - Khajura 8 Surkhet': 'Nepal Rastriya Secondary School',
        'Nepal Rastriya Secondary School- Khajura 8 Surkhet': 'Nepal Rastriya Secondary School',
        'Nepal Rastriya Secondary School-Khajura 8 Surkhet': 'Nepal Rastriya Secondary School',
        
        # Raina Devi Basic School variations
        'RAINA DEVI BASIC SCHOOL, NARAYAN 11, KANDA, DAILEKH': 'Raina Devi Basic School',
        
        # Secondary School variations (Janakpurdham)
        'Ma vi Basabitti janakpurdham - 22': 'Secondary School',
    }
    
    # Apply exact string replacement
    df['school'] = df['school'].replace(school_name_mapping)
    
    return df

def clean_grade_values(df):
    """Clean and standardize grade values to avoid duplicates"""
    if 'grade' in df.columns:
        # Strip whitespace and convert to string
        df['grade'] = df['grade'].astype(str).str.strip()
        
        # Standardize grade format (remove 'Grade ' prefix if present)
        df['grade'] = df['grade'].str.replace('Grade ', '', case=False, regex=False)
        df['grade'] = df['grade'].str.replace('grade ', '', case=False, regex=False)
        
        # Remove any extra spaces
        df['grade'] = df['grade'].str.strip()
        
        # Handle common variations
        grade_mapping = {
            'class 1': '1',
            'class 2': '2',
            'class 3': '3',
            'class 4': '4',
            'class 5': '5',
            'class 6': '6',
            'class 7': '7',
            'class 8': '8',
        }
        
        df['grade'] = df['grade'].str.lower().replace(grade_mapping).str.strip()
    
    return df

# -------------------------
# HELPER FUNCTIONS
# -------------------------
def get_school_info(df):
    """Extract and organize school information by project and district"""
    schools = df['school'].unique()
    school_info = {}
    
    for school in schools:
        # Try to get metadata for the school
        if school in SCHOOL_METADATA:
            project = SCHOOL_METADATA[school].get("project", "Unknown")
            district = SCHOOL_METADATA[school].get("district", "Unknown")
            address = SCHOOL_METADATA[school].get("address", "")
        else:
            # If not in metadata, set as unknown
            project = "Unknown"
            district = "Unknown"
            address = ""
        
        # Organize by project -> district
        if project not in school_info:
            school_info[project] = {}
        if district not in school_info[project]:
            school_info[project][district] = []
        
        # Store school with its address
        school_info[project][district].append({
            "name": school,
            "address": address
        })
    
    return school_info

# -------------------------
# SIDEBAR STYLING
# -------------------------
st.markdown("""
    <style>
    .dataset-card {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .school-section {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #1f77b4;
        padding-left: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR DATA SOURCE SELECTION
# -------------------------
st.sidebar.title("📊 Survey Dashboard")
st.sidebar.markdown("---")
st.sidebar.header("📁 Dataset Selection")

# Create radio buttons for dataset selection with better labels
dataset_labels = list(DATASET_CONFIG.keys())
selected_label = st.sidebar.radio(
    "Choose dataset:",
    dataset_labels,
    help="Select which survey records to analyze"
)

# Get the corresponding file
selected_dataset = DATASET_CONFIG[selected_label]["file"]

# Display dataset information card
dataset_info = DATASET_CONFIG[selected_label]
st.sidebar.markdown(f"""
<div class="dataset-card">
    <h4>{dataset_info['icon']} {selected_label}</h4>
    <p style='font-size: 0.85rem; color: #666;'>{dataset_info['description']}</p>
</div>
""", unsafe_allow_html=True)

# Load the selected dataset (raw data - cached)
df_raw = load_data_cached(selected_dataset)

# Clean the data (always runs with latest cleaning logic - NOT cached)
df = clean_school_names(df_raw.copy())
df = clean_grade_values(df)

# Display record count
st.sidebar.metric("📝 Total Records", len(df))

# Add cache clear button
if st.sidebar.button("🔄 Clear Cache & Reload"):
    st.cache_data.clear()
    st.rerun()

# Add debug expander to show unique schools
with st.sidebar.expander("🔍 Debug: View All Unique Schools", expanded=False):
    unique_schools = sorted(df['school'].unique())
    st.write(f"**Total Unique Schools: {len(unique_schools)}**")
    st.write("**Raw school names from data:**")
    for school in unique_schools:
        count = len(df[df['school'] == school])
        # Show the exact string with quotes to see any hidden characters
        st.code(f'"{school}" ({count} records)')
    
    st.write("---")
    st.write("**Expected school names from metadata:**")
    for school in sorted(SCHOOL_METADATA.keys()):
        st.text(f"• {school}")

st.sidebar.markdown("---")

# -------------------------
# SIDEBAR SCHOOL SELECTION
# -------------------------
st.sidebar.header("🏫 School Selection")

# Get school information organized by project and location
school_info = get_school_info(df)

# Selection mode
selection_mode = st.sidebar.radio(
    "Selection Mode:",
    ["All Schools", "Custom Selection"],
    help="Choose how to filter schools"
)

selected_schools = []

if selection_mode == "All Schools":
    selected_schools = df['school'].unique().tolist()
    st.sidebar.success(f"✅ All {len(selected_schools)} schools selected")
else:
    st.sidebar.markdown("**Select schools by project and district:**")
    
    # Organize by project
    for project, districts in sorted(school_info.items()):
        with st.sidebar.expander(f"📂 {project} Project", expanded=True):
            # Add "Select All" for this project
            project_schools = []
            for district, schools in districts.items():
                project_schools.extend([s["name"] for s in schools])
            
            select_all_project = st.checkbox(
                f"Select all {project} schools ({len(project_schools)})",
                key=f"all_{project}"
            )
            
            # Organize by district within project
            for district, schools in sorted(districts.items()):
                st.markdown(f"**📍 {district} District**")
                
                # Individual school checkboxes with address
                for school_data in sorted(schools, key=lambda x: x["name"]):
                    school_name = school_data["name"]
                    school_address = school_data["address"]
                    
                    # Create display label with address
                    if school_address:
                        display_label = f"{school_name}"
                        help_text = f"📍 {school_address}, {district}"
                    else:
                        display_label = school_name
                        help_text = f"📍 {district}"
                    
                    is_selected = select_all_project or st.checkbox(
                        display_label,
                        value=select_all_project,
                        key=f"school_{school_name}",
                        disabled=select_all_project,
                        help=help_text
                    )
                    if is_selected:
                        selected_schools.append(school_name)
    
    # Remove duplicates
    selected_schools = list(set(selected_schools))
    
    if selected_schools:
        st.sidebar.info(f"✅ {len(selected_schools)} school(s) selected")
    else:
        st.sidebar.warning("⚠️ No schools selected")

# -------------------------
# DATA FILTERING LOGIC
# -------------------------
def apply_filters(df):
    if selected_schools:
        return df[df['school'].isin(selected_schools)]
    return df

df_filtered = apply_filters(df)

# Show warning if no data after filtering
if len(df_filtered) == 0:
    st.warning("⚠️ No data available with current filters. Please adjust your selection.")
    st.stop()

# -------------------------
# MAIN CONTENT HEADER
# -------------------------
st.title("📊 School Survey Analysis Dashboard")
st.markdown(f"**Dataset:** {selected_label} | **Records:** {len(df_filtered):,} students from {df_filtered['school'].nunique()} schools")
st.markdown("---")

# -------------------------
# TABS STRUCTURE
# -------------------------
tab_overview, tab_numeracy, tab_reading = st.tabs([
    "📊 Overview",
    "🧮 Numeracy Analysis",
    "📖 Reading Analysis"
])

# -------------------------
# OVERVIEW TAB
# -------------------------
with tab_overview:
    st.header("📊 Survey Data Overview")

    overview_results = sa.plot_overview_summary(
        df, 
        sa.numeracy_ids, 
        sa.long_eng_reading_ids, 
        sa.long_nep_reading_ids
    )

    # Display Summary Metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Students", overview_results["total_students"])
    with col2:
        st.metric("🏫 Schools", overview_results["total_schools"])
    with col3:
        # Use actual column name 'studentGender'
        if 'studentGender' in df.columns:
            female_count = df['studentGender'].value_counts().get('Female', 0)
            st.metric("👧 Female", f"{female_count:,}")
        else:
            st.metric("👧 Female", "N/A")
    with col4:
        if 'studentGender' in df.columns:
            male_count = df['studentGender'].value_counts().get('Male', 0)
            st.metric("👦 Male", f"{male_count:,}")
        else:
            st.metric("👦 Male", "N/A")

    st.markdown("---")

    # Performance Summary
    st.subheader("⭐ Average Performance Summary")
    st.plotly_chart(overview_results["fig_performance"], width='stretch', key="overview_performance")

    st.markdown("---")

    # School Comparison
    st.subheader("🏆 Competency Comparison Across Schools")
    st.plotly_chart(overview_results["fig_summary"], width='stretch', key="overview_summary")

    st.markdown("---")

    # Demographics
    st.subheader("👥 Demographics")
    row1_col1, row1_col2 = st.columns([1, 2])
    with row1_col1:
        st.plotly_chart(overview_results["fig_gender"], width='stretch', key="overview_gender")
    with row1_col2:
        st.plotly_chart(overview_results["fig_grade"], width='stretch', key="overview_grade")

    st.markdown("---")

    # Age Distribution
    st.subheader("⏳ Age Distribution")
    st.plotly_chart(overview_results["fig_age"], width='stretch', key="overview_age")
    
# -------------------------
# NUMERACY TAB
# -------------------------
with tab_numeracy:
    st.header("🧮 Numeracy Skills Analysis")

    numeracy_analysis = sa.numeracy_analysis(df_filtered, sa.numeracy_ids)
    plots = sa.plot_numeracy_results(numeracy_analysis)

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Students Analyzed", len(df_filtered))
    with col2:
        st.metric("🏫 Schools", df_filtered['school'].nunique())
    with col3:
        # Calculate average completion across all numeracy tasks
        avg_completion = (
            numeracy_analysis['analysis_one']['percentage_meeting'] +
            numeracy_analysis['analysis_two']['percentage_meeting'] +
            numeracy_analysis['analysis_three']['percentage_meeting'] +
            numeracy_analysis['analysis_four']['percentage_meeting'] +
            numeracy_analysis['analysis_five']['percentage_meeting']
        ) / 5
        st.metric("📈 Avg Completion Rate", f"{avg_completion:.1f}%")

    st.markdown("---")

    st.subheader("Task Completion Rates")
    st.plotly_chart(plots['fig_overall'], width='stretch', key="num_overall")

    st.subheader("Performance by Gender")
    st.plotly_chart(plots['fig_gender'], width='stretch', key="num_gender")

    if plots['fig_age']:
        st.subheader("Age-wise Progression")
        st.plotly_chart(plots['fig_age'], width='stretch', key="num_age")

    if plots['fig_grade']:
        st.subheader("Grade-level Performance")
        st.plotly_chart(plots['fig_grade'], width='stretch', key="num_grade")

# -------------------------
# READING TAB
# -------------------------
with tab_reading:
    st.header("📖 Reading Proficiency Analysis")

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Students Analyzed", len(df_filtered))
    with col2:
        st.metric("🏫 Schools", df_filtered['school'].nunique())
    with col3:
        st.metric("📚 Languages", "2 (English & Nepali)")

    st.markdown("---")

    # Sub-tabs for English and Nepali
    tab_eng, tab_nep = st.tabs([
        "🇬🇧 English Reading",
        "🇳🇵 Nepali Reading"
    ])

    # English Reading Analysis
    with tab_eng:
        st.subheader("English Reading Performance")
        
        eng_res = sa.reading_analysis(df_filtered, sa.long_eng_reading_ids, lang="English")
        reading_plots_eng = sa.plot_reading_results(eng_res, df_filtered)
        
        st.plotly_chart(reading_plots_eng["fig_overall"], width='stretch', key="eng_overall")
        st.plotly_chart(reading_plots_eng["fig_gender"], width='stretch', key="eng_gender")
        
        if reading_plots_eng["fig_age"]:
            st.plotly_chart(reading_plots_eng["fig_age"], width='stretch', key="eng_age")
        
        if reading_plots_eng["fig_grade"]:
            st.plotly_chart(reading_plots_eng["fig_grade"], width='stretch', key="eng_grade")

    # Nepali Reading Analysis
    with tab_nep:
        st.subheader("Nepali Reading Performance")
        
        nep_res = sa.reading_analysis(df_filtered, sa.long_nep_reading_ids, lang="Nepali")
        reading_plots_nep = sa.plot_reading_results(nep_res, df_filtered)
        
        st.plotly_chart(reading_plots_nep["fig_overall"], width='stretch', key="nep_overall")
        st.plotly_chart(reading_plots_nep["fig_gender"], width='stretch', key="nep_gender")
        
        if reading_plots_nep["fig_age"]:
            st.plotly_chart(reading_plots_nep["fig_age"], width='stretch', key="nep_age")
        
        if reading_plots_nep["fig_grade"]:
            st.plotly_chart(reading_plots_nep["fig_grade"], width='stretch', key="nep_grade")

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("*Dashboard for analyzing school survey data across numeracy and reading competencies*")