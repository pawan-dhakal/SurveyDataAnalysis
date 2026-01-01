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

    # Always show: Header metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("👥 Students", len(df_filtered))
    with col2:
        st.metric("🏫 Schools", df_filtered['school'].nunique())
    with col3:
        if 'studentGender' in df_filtered.columns:
            female_count = df_filtered['studentGender'].value_counts().get('Female', 0)
            st.metric("👧 Female", f"{female_count:,}")
        else:
            st.metric("👧 Female", "N/A")
    with col4:
        if 'studentGender' in df_filtered.columns:
            male_count = df_filtered['studentGender'].value_counts().get('Male', 0)
            st.metric("👦 Male", f"{male_count:,}")
        else:
            st.metric("👦 Male", "N/A")
    with col5:
        if 'studentAge' in df_filtered.columns:
            age_min = int(df_filtered['studentAge'].min())
            age_max = int(df_filtered['studentAge'].max())
            st.metric("⏳ Age Range", f"{age_min}-{age_max} yrs")
        else:
            st.metric("⏳ Age Range", "N/A")

    st.markdown("---")

    # Always show: Demographics
    st.subheader("👥 Demographics")
    
    # Generate demographic figures
    if 'studentGender' in df_filtered.columns:
        gender_counts = df_filtered['studentGender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig_gender = px.pie(
            gender_counts,
            names='Gender',
            values='Count',
            title="Gender Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig_gender.update_traces(
            textinfo='label+percent+value',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
    else:
        fig_gender = None
    
    if 'grade' in df_filtered.columns:
        df_filtered['grade'] = pd.Categorical(df_filtered['grade'], 
                                              categories=sorted(df_filtered['grade'].dropna().unique()), 
                                              ordered=True)
        grade_counts = df_filtered['grade'].value_counts().sort_index().reset_index()
        grade_counts.columns = ['Grade', 'Count']
        grade_counts['Percentage'] = (grade_counts['Count'] / len(df_filtered) * 100).round(1)
        grade_counts['Label'] = grade_counts.apply(lambda row: f"{row['Count']} ({row['Percentage']}%)", axis=1)
        
        fig_grade = px.bar(
            grade_counts,
            x='Grade',
            y='Count',
            text='Label',
            title="Grade Distribution",
            color='Grade',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_grade.update_traces(
            textposition='outside',
            hovertemplate='<b>Grade %{x}</b><br>Count: %{y}<extra></extra>'
        )
        fig_grade.update_layout(showlegend=False)
    else:
        fig_grade = None
    
    if 'studentAge' in df_filtered.columns:
        fig_age = px.histogram(
            df_filtered,
            x="studentAge",
            title="Age Distribution",
            nbins=15,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_age.update_traces(
            hovertemplate='<b>Age: %{x}</b><br>Count: %{y}<extra></extra>'
        )
    else:
        fig_age = None
    
    # Display demographics in columns
    demo_col1, demo_col2, demo_col3 = st.columns([1, 2, 2])
    with demo_col1:
        if fig_gender:
            st.plotly_chart(fig_gender, width='stretch', key="demo_gender")
    with demo_col2:
        if fig_grade:
            st.plotly_chart(fig_grade, width='stretch', key="demo_grade")
    with demo_col3:
        if fig_age:
            st.plotly_chart(fig_age, width='stretch', key="demo_age")

    st.markdown("---")

    # Conditional content based on number of schools selected
    num_schools = df_filtered['school'].nunique()
    
    if num_schools > 1:
        # MULTIPLE SCHOOLS VIEW
        st.subheader("⭐ Average Performance Summary")
        
        # Calculate average performance across selected schools
        numeracy_analysis_all = sa.numeracy_analysis(df_filtered, sa.numeracy_ids)
        eng_analysis_all = sa.reading_analysis(df_filtered, sa.long_eng_reading_ids, lang="English")
        nep_analysis_all = sa.reading_analysis(df_filtered, sa.long_nep_reading_ids, lang="Nepali")
        
        avg_perf_df = pd.DataFrame({
            "Competency": ["Numeracy", "English Reading", "Nepali Reading"],
            "Percentage": [
                numeracy_analysis_all['analysis_five']['percentage_meeting'],
                eng_analysis_all['analysis_four']['percentage_meeting'],
                nep_analysis_all['analysis_four']['percentage_meeting']
            ]
        })
        
        fig_avg_perf = px.bar(
            avg_perf_df,
            x="Competency",
            y="Percentage",
            text="Percentage",
            color="Competency",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_avg_perf.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        fig_avg_perf.update_layout(
            yaxis=dict(range=[0, 100]),
            showlegend=False,
            title="Average Performance Across Selected Schools"
        )
        st.plotly_chart(fig_avg_perf, width='stretch', key="avg_perf")
        
        st.markdown("---")
        
        # School comparison
        st.subheader("🏆 Competency Comparison Across Schools")
        
        school_summary = []
        for school in sorted(df_filtered['school'].unique()):
            school_df = df_filtered[df_filtered['school'] == school]
            num_res = sa.numeracy_analysis(school_df, sa.numeracy_ids, printText=False)
            eng_res = sa.reading_analysis(school_df, sa.long_eng_reading_ids, lang="English", printText=False)
            nep_res = sa.reading_analysis(school_df, sa.long_nep_reading_ids, lang="Nepali", printText=False)
            
            school_summary.append({
                "School": school,
                "Numeracy": num_res['analysis_five']['percentage_meeting'],
                "English Reading": eng_res['analysis_four']['percentage_meeting'],
                "Nepali Reading": nep_res['analysis_four']['percentage_meeting']
            })
        
        summary_df = pd.DataFrame(school_summary)
        summary_long = summary_df.melt(id_vars=['School'], var_name='Competency', value_name='Percentage')
        
        fig_comparison = px.bar(
            summary_long,
            x="School",
            y="Percentage",
            color="Competency",
            barmode="group",
            text="Percentage",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_comparison.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        fig_comparison.update_layout(
            yaxis=dict(range=[0, 100]),
            xaxis_tickangle=-45,
            title="School Performance Comparison"
        )
        st.plotly_chart(fig_comparison, width='stretch', key="school_comparison")
        
    else:
        # SINGLE SCHOOL VIEW
        school_name = df_filtered['school'].unique()[0]
        st.subheader(f"📊 Performance Summary: {school_name}")
        
        # Run analyses
        numeracy_res = sa.numeracy_analysis(df_filtered, sa.numeracy_ids, printText=False)
        eng_res = sa.reading_analysis(df_filtered, sa.long_eng_reading_ids, lang="English", printText=False)
        nep_res = sa.reading_analysis(df_filtered, sa.long_nep_reading_ids, lang="Nepali", printText=False)
        
        # Overall performance metrics with PIE CHARTS
        st.markdown("### 🎯 Overall Competency Achievement")
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            # Numeracy Pie Chart
            num_achieved = numeracy_res['analysis_five']['count_meeting']
            num_total = numeracy_res['analysis_five']['total_students']
            num_not_achieved = num_total - num_achieved
            
            fig_num_pie = px.pie(
                values=[num_achieved, num_not_achieved],
                names=['Achieved', 'Not Achieved'],
                title=f"🧮 Foundational Numeracy<br>{numeracy_res['analysis_five']['percentage_meeting']:.1f}%",
                color_discrete_sequence=['#2ecc71', '#e74c3c']
            )
            fig_num_pie.update_traces(textinfo='value+percent')
            st.plotly_chart(fig_num_pie, use_container_width=True, key="num_pie")
        
        with perf_col2:
            # English Reading Pie Chart
            eng_achieved = eng_res['analysis_four']['count_meeting']
            eng_total = eng_res['analysis_four']['total_students']
            eng_not_achieved = eng_total - eng_achieved
            
            fig_eng_pie = px.pie(
                values=[eng_achieved, eng_not_achieved],
                names=['Achieved', 'Not Achieved'],
                title=f"📖 English Reading<br>{eng_res['analysis_four']['percentage_meeting']:.1f}%",
                color_discrete_sequence=['#3498db', '#e67e22']
            )
            fig_eng_pie.update_traces(textinfo='value+percent')
            st.plotly_chart(fig_eng_pie, use_container_width=True, key="eng_pie")
        
        with perf_col3:
            # Nepali Reading Pie Chart
            nep_achieved = nep_res['analysis_four']['count_meeting']
            nep_total = nep_res['analysis_four']['total_students']
            nep_not_achieved = nep_total - nep_achieved
            
            fig_nep_pie = px.pie(
                values=[nep_achieved, nep_not_achieved],
                names=['Achieved', 'Not Achieved'],
                title=f"📖 Nepali Reading<br>{nep_res['analysis_four']['percentage_meeting']:.1f}%",
                color_discrete_sequence=['#9b59b6', '#e74c3c']
            )
            fig_nep_pie.update_traces(textinfo='value+percent')
            st.plotly_chart(fig_nep_pie, use_container_width=True, key="nep_pie")
        
        st.markdown("---")
        
        # NUMERACY BREAKDOWN
        st.subheader("🧮 Numeracy Performance Breakdown")
        
        # Gender breakdown for numeracy
        num_gender_data = []
        for gender in ['Male', 'Female']:
            if gender in numeracy_res['analysis_five']['gender_results']:
                num_gender_data.append({
                    'Gender': gender,
                    'Percentage': numeracy_res['analysis_five']['gender_results'][gender]['percentage']
                })
        
        if num_gender_data:
            num_gender_df = pd.DataFrame(num_gender_data)
            fig_num_gender = px.bar(
                num_gender_df,
                x='Gender',
                y='Percentage',
                text='Percentage',
                color='Gender',
                color_discrete_sequence=px.colors.qualitative.Set1,
                title="Foundational Numeracy by Gender"
            )
            fig_num_gender.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_num_gender.update_layout(yaxis=dict(range=[0, 100]), showlegend=False)
        else:
            fig_num_gender = None
        
        # Age breakdown for numeracy
        num_age_data = []
        if 'analysis_age' in numeracy_res and 'foundational_numeracy' in numeracy_res['analysis_age']:
            for age, data in numeracy_res['analysis_age']['foundational_numeracy'].items():
                num_age_data.append({
                    'Age': age,
                    'Percentage': data['percentage']
                })
        
        if num_age_data:
            num_age_df = pd.DataFrame(num_age_data).sort_values('Age')
            fig_num_age = px.line(
                num_age_df,
                x='Age',
                y='Percentage',
                markers=True,
                title="Foundational Numeracy by Age"
            )
            fig_num_age.update_traces(
                text=num_age_df['Percentage'].apply(lambda x: f"{x:.1f}%"),
                textposition='top center'
            )
            fig_num_age.update_layout(yaxis=dict(range=[0, 110]))
        else:
            fig_num_age = None
        
        # Grade breakdown for numeracy
        num_grade_data = []
        if 'analysis_grade' in numeracy_res and 'foundational_numeracy' in numeracy_res['analysis_grade']:
            for grade, data in numeracy_res['analysis_grade']['foundational_numeracy'].items():
                num_grade_data.append({
                    'Grade': grade,
                    'Percentage': data['percentage']
                })
        
        if num_grade_data:
            num_grade_df = pd.DataFrame(num_grade_data).sort_values('Grade')
            fig_num_grade = px.bar(
                num_grade_df,
                x='Grade',
                y='Percentage',
                text='Percentage',
                title="Foundational Numeracy by Grade",
                color='Grade',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_num_grade.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_num_grade.update_layout(yaxis=dict(range=[0, 110]), showlegend=False)
        else:
            fig_num_grade = None
        
        num_col1, num_col2, num_col3 = st.columns(3)
        with num_col1:
            if fig_num_gender:
                st.plotly_chart(fig_num_gender, width='stretch', key="single_num_gender")
        with num_col2:
            if fig_num_age:
                st.plotly_chart(fig_num_age, width='stretch', key="single_num_age")
        with num_col3:
            if fig_num_grade:
                st.plotly_chart(fig_num_grade, width='stretch', key="single_num_grade")
        
        st.markdown("---")
        
        # ENGLISH READING BREAKDOWN
        st.subheader("📖 English Reading Performance Breakdown")
        
        # Gender breakdown for English reading
        eng_gender_data = []
        if 'analysis_gender' in eng_res and eng_res['analysis_gender']:
            for gender, metrics in eng_res['analysis_gender'].items():
                eng_gender_data.append({
                    'Gender': gender,
                    'Percentage': metrics['foundational']
                })
        
        if eng_gender_data:
            eng_gender_df = pd.DataFrame(eng_gender_data)
            fig_eng_gender = px.bar(
                eng_gender_df,
                x='Gender',
                y='Percentage',
                text='Percentage',
                color='Gender',
                color_discrete_sequence=px.colors.qualitative.Set1,
                title="Foundational English Reading by Gender"
            )
            fig_eng_gender.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_eng_gender.update_layout(yaxis=dict(range=[0, 100]), showlegend=False)
        else:
            fig_eng_gender = None
            st.info("No gender breakdown data available for English reading")
        
        # Age breakdown for English reading
        eng_age_data = []
        if 'analysis_age' in eng_res and 'foundational' in eng_res['analysis_age']:
            for age, data in eng_res['analysis_age']['foundational'].items():
                eng_age_data.append({
                    'Age': age,
                    'Percentage': data['percentage']
                })
        
        if eng_age_data:
            eng_age_df = pd.DataFrame(eng_age_data).sort_values('Age')
            fig_eng_age = px.line(
                eng_age_df,
                x='Age',
                y='Percentage',
                markers=True,
                title="Foundational English Reading by Age"
            )
            fig_eng_age.update_traces(
                text=eng_age_df['Percentage'].apply(lambda x: f"{x:.1f}%"),
                textposition='top center'
            )
            fig_eng_age.update_layout(yaxis=dict(range=[0, 110]))
        else:
            fig_eng_age = None
        
        # Grade breakdown for English reading
        eng_grade_data = []
        if 'analysis_grade' in eng_res and 'foundational' in eng_res['analysis_grade']:
            for grade, data in eng_res['analysis_grade']['foundational'].items():
                eng_grade_data.append({
                    'Grade': grade,
                    'Percentage': data['percentage']
                })
        
        if eng_grade_data:
            eng_grade_df = pd.DataFrame(eng_grade_data).sort_values('Grade')
            fig_eng_grade = px.bar(
                eng_grade_df,
                x='Grade',
                y='Percentage',
                text='Percentage',
                title="Foundational English Reading by Grade",
                color='Grade',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_eng_grade.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_eng_grade.update_layout(yaxis=dict(range=[0, 110]), showlegend=False)
        else:
            fig_eng_grade = None
        
        eng_col1, eng_col2, eng_col3 = st.columns(3)
        with eng_col1:
            if fig_eng_gender:
                st.plotly_chart(fig_eng_gender, width='stretch', key="single_eng_gender")
        with eng_col2:
            if fig_eng_age:
                st.plotly_chart(fig_eng_age, width='stretch', key="single_eng_age")
        with eng_col3:
            if fig_eng_grade:
                st.plotly_chart(fig_eng_grade, width='stretch', key="single_eng_grade")
        
        st.markdown("---")
        
        # NEPALI READING BREAKDOWN
        st.subheader("📖 Nepali Reading Performance Breakdown")
        
        # Gender breakdown for Nepali reading
        nep_gender_data = []
        if 'analysis_gender' in nep_res and nep_res['analysis_gender']:
            for gender, metrics in nep_res['analysis_gender'].items():
                nep_gender_data.append({
                    'Gender': gender,
                    'Percentage': metrics['foundational']
                })
        
        if nep_gender_data:
            nep_gender_df = pd.DataFrame(nep_gender_data)
            fig_nep_gender = px.bar(
                nep_gender_df,
                x='Gender',
                y='Percentage',
                text='Percentage',
                color='Gender',
                color_discrete_sequence=px.colors.qualitative.Set1,
                title="Foundational Nepali Reading by Gender"
            )
            fig_nep_gender.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_nep_gender.update_layout(yaxis=dict(range=[0, 100]), showlegend=False)
        else:
            fig_nep_gender = None
            st.info("No gender breakdown data available for Nepali reading")
        
        # Age breakdown for Nepali reading
        nep_age_data = []
        if 'analysis_age' in nep_res and 'foundational' in nep_res['analysis_age']:
            for age, data in nep_res['analysis_age']['foundational'].items():
                nep_age_data.append({
                    'Age': age,
                    'Percentage': data['percentage']
                })
        
        if nep_age_data:
            nep_age_df = pd.DataFrame(nep_age_data).sort_values('Age')
            fig_nep_age = px.line(
                nep_age_df,
                x='Age',
                y='Percentage',
                markers=True,
                title="Foundational Nepali Reading by Age"
            )
            fig_nep_age.update_traces(
                text=nep_age_df['Percentage'].apply(lambda x: f"{x:.1f}%"),
                textposition='top center'
            )
            fig_nep_age.update_layout(yaxis=dict(range=[0, 110]))
        else:
            fig_nep_age = None
        
        # Grade breakdown for Nepali reading
        nep_grade_data = []
        if 'analysis_grade' in nep_res and 'foundational' in nep_res['analysis_grade']:
            for grade, data in nep_res['analysis_grade']['foundational'].items():
                nep_grade_data.append({
                    'Grade': grade,
                    'Percentage': data['percentage']
                })
        
        if nep_grade_data:
            nep_grade_df = pd.DataFrame(nep_grade_data).sort_values('Grade')
            fig_nep_grade = px.bar(
                nep_grade_df,
                x='Grade',
                y='Percentage',
                text='Percentage',
                title="Foundational Nepali Reading by Grade",
                color='Grade',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_nep_grade.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_nep_grade.update_layout(yaxis=dict(range=[0, 110]), showlegend=False)
        else:
            fig_nep_grade = None
        
        nep_col1, nep_col2, nep_col3 = st.columns(3)
        with nep_col1:
            if fig_nep_gender:
                st.plotly_chart(fig_nep_gender, width='stretch', key="single_nep_gender")
        with nep_col2:
            if fig_nep_age:
                st.plotly_chart(fig_nep_age, width='stretch', key="single_nep_age")
        with nep_col3:
            if fig_nep_grade:
                st.plotly_chart(fig_nep_grade, width='stretch', key="single_nep_grade")
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