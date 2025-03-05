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

data_path = 'combined_cleaned_survey_records.csv'
df = load_data_cached(data_path)

# -------------------------
# SIDEBAR: ENHANCED FILTERS
# -------------------------
st.sidebar.header("Filter Your Data")

# Reset Filters Button
if st.sidebar.button("Reset Filters"):
    st.session_state.clear()

# Demographics Filters
with st.sidebar.expander("Demographics", expanded=True):
    st.markdown("*Filter by student demographics*")
    gender_options = sorted(df['studentGender'].unique().tolist())
    selected_genders = st.multiselect(
        "Select Gender(s)", 
        options=gender_options, 
        default=gender_options,
        key="gender"
    )
    
    age_min, age_max = int(df['studentAge'].min()), int(df['studentAge'].max())
    selected_age_range = st.slider(
        "Select Age Range", 
        age_min, age_max, 
        (age_min, age_max), 
        key="age"
    )
    st.markdown(f"Selected: {selected_age_range[0]} - {selected_age_range[1]} years")

# School & Grade Filters
with st.sidebar.expander("School & Grade", expanded=True):
    st.markdown("*Filter by school and grade level*")
    school_options = ["All"] + sorted(df['school'].unique().tolist())
    selected_school = st.selectbox(
        "Select School (Detailed View)", 
        options=school_options, 
        key="school"
    )
    
    grade_options = sorted(df['grade'].unique().tolist())
    selected_grades = st.multiselect(
        "Select Grade(s)", 
        options=grade_options, 
        default=grade_options,
        key="grade"
    )

# Comparison Options
with st.sidebar.expander("Comparative Analysis", expanded=False):
    st.markdown("*Compare multiple schools or languages*")
    comparison_schools = st.multiselect(
        "Compare Schools", 
        options=school_options[1:], 
        key="comp_schools"
    )
    language_options = ["English", "Nepali"]
    comparison_languages = st.multiselect(
        "Compare Languages", 
        options=language_options, 
        default=["English"],
        key="comp_langs"
    )

st.sidebar.info("Filters apply globally. Use 'Comparative Analysis' for multi-school views.")

# -------------------------
# APPLY FILTERS
# -------------------------
df_filtered = df.copy()
if selected_school != "All":
    df_filtered = df_filtered[df_filtered['school'] == selected_school]
if selected_grades:
    df_filtered = df_filtered[df_filtered['grade'].isin(selected_grades)]
if selected_genders:
    df_filtered = df_filtered[df_filtered['studentGender'].isin(selected_genders)]
df_filtered = df_filtered[
    (df_filtered['studentAge'] >= selected_age_range[0]) & 
    (df_filtered['studentAge'] <= selected_age_range[1])
]

# -------------------------
# ANALYSIS PARAMETERS
# -------------------------
numeracy_ids = ["FL23_cleaned1", "FL23_cleaned2", "FL23_cleaned3", "FL23_cleaned4", "FL23_cleaned5", \
                 "FL23_cleaned6", "FL24_cleaned1", "FL24_cleaned2", "FL24_cleaned3", "FL24_cleaned4", "FL24_cleaned5", \
                 "FL25_cleaned1", "FL25_cleaned2", "FL25_cleaned3", "FL25_cleaned4", "FL25_cleaned5", \
                 "FL26", "FL26C", "FL27_cleaned1", "FL27_cleaned2", "FL27_cleaned3", "FL27_cleaned4"] #dropped "FL27_cleaned5" 

eng_reading_ids = ['FL13_cleaned', 'FL15', 'FL17', 'FL19_cleaned', 'FL21B_cleaned1', 
                   'FL21B_cleaned2', 'FL21B_cleaned3', 'FL21B_cleaned4', 'FL21B_cleaned5']
nep_reading_ids = ["FL21G_cleaned", "FL21I", "FL21K", "FL21O_cleaned", 
                   "FL22_cleaned1", "FL22_cleaned2", "FL22_cleaned3", "FL22_cleaned4", "FL22_cleaned5"]
total_words = {"English": 61, "Nepali": 48}

# -------------------------
# TAB LAYOUT
# -------------------------
st.info("Welcome! Use the sidebar to filter data, then explore tabs for insights.")
tabs = st.tabs(["Overview", "Detailed Analysis", "Comparative Analysis"])

# -------------------------
# TAB 1: OVERVIEW
# -------------------------
with tabs[0]:
    st.title("School Survey Dashboard")
    st.markdown("### Key Metrics")
    
    summary = sa.foundational_skills_summary(
        df_filtered, eng_reading_ids[3:9], numeracy_ids, total_words["English"]
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Students (Age 7-14)", summary["total_records_overall"])
    with col2:
        st.metric("Reading Skills (%)", f"{summary['reading_foundational_overall']:.1f}%")
    with col3:
        st.metric("Numeracy Skills (%)", f"{summary['numeracy_foundational_overall']:.1f}%")
    
    with st.expander("Gender Parity (Reading)"):
        st.dataframe(pd.DataFrame(summary["reading_gender_parity_overall"]).T)
    
    if "total_records_grade_2_3" in summary:
        st.markdown("#### Grade 2/3 Metrics")
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("Total Grade 2/3", summary["total_records_grade_2_3"])
        with col5:
            st.metric("Reading (%)", f"{summary['reading_foundational_grade']:.1f}%")
        with col6:
            st.metric("Numeracy (%)", f"{summary['numeracy_foundational_grade']:.1f}%")
    
    with st.expander("Raw Data Preview"):
        st.dataframe(df_filtered.head(100), use_container_width=True)

# -------------------------
# TAB 2: DETAILED ANALYSIS (SINGLE SCHOOL)
# -------------------------
with tabs[1]:
    st.header(f"Detailed Analysis: {selected_school if selected_school != 'All' else 'All Schools'}")
    if df_filtered.empty:
        st.warning("No data matches your filters.")
    else:
        # Numeracy
        st.subheader("Numeracy Insights")
        num_results = sa.numeracy_analysis(df_filtered, numeracy_ids, printText=False)
        st.markdown(sa.get_formatted_numeracy_results(num_results))
        figs_num = sa.plot_numeracy_results(num_results)
        st.plotly_chart(figs_num["fig_overall"], use_container_width=True)
        
        with st.expander("Breakdowns"):
            col1, col2 = st.columns(2)
            with col1:
                if figs_num["fig_gender"]:
                    st.plotly_chart(figs_num["fig_gender"], use_container_width=True)
            with col2:
                if figs_num["fig_age"]:
                    st.plotly_chart(figs_num["fig_age"], use_container_width=True)
            if figs_num["fig_grade"]:
                st.plotly_chart(figs_num["fig_grade"], use_container_width=True)
        
        # Reading
        st.subheader("Reading Insights")
        lang = st.selectbox("Language", language_options, key="detail_lang")
        reading_ids = eng_reading_ids[3:9] if lang == "English" else nep_reading_ids[3:9]
        read_results = sa.reading_analysis(df_filtered, reading_ids, total_words[lang], lang=lang, printText=False)
        st.markdown(sa.get_formatted_reading_results(read_results, lang))
        read_fig = sa.plot_reading_results(read_results, lang, selected_school)
        st.plotly_chart(read_fig, use_container_width=True)
        
        with st.expander("Breakdowns"):
            breakdown = sa.plot_reading_breakdown(read_results["analysis_age"], read_results["analysis_gender"])
            col3, col4 = st.columns(2)
            with col3:
                if breakdown["fig_reading_age"]:
                    st.plotly_chart(breakdown["fig_reading_age"], use_container_width=True)
            with col4:
                if breakdown["fig_reading_gender"]:
                    st.plotly_chart(breakdown["fig_reading_gender"], use_container_width=True)

# -------------------------
# TAB 3: COMPARATIVE ANALYSIS
# -------------------------
with tabs[2]:
    st.header("Comparative Analysis")
    if not comparison_schools and not comparison_languages:
        st.warning("Select schools or languages in the sidebar to compare.")
    else:
        # School Comparison (Numeracy)
        if comparison_schools:
            st.subheader("Numeracy Across Schools")
            comp_data = []
            for school in comparison_schools:
                df_comp = df[df["school"] == school]
                if not df_comp.empty:
                    res = sa.numeracy_analysis(df_comp, numeracy_ids, printText=False)
                    comp_data.append({
                        "School": school,
                        "Percentage": res["analysis_five"]["percentage_meeting"],
                        "Students": res["analysis_five"]["total_students"]
                    })
            if comp_data:
                df_comp = pd.DataFrame(comp_data)
                fig = px.bar(
                    df_comp, x="School", y="Percentage", text="Percentage",
                    title="Foundational Numeracy by School",
                    color="Percentage", color_continuous_scale="Viridis"
                )
                fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_comp)
        
        # Language Comparison (Reading)
        if len(comparison_languages) > 1:
            st.subheader("Reading Across Languages")
            comp_read_data = []
            for lang in comparison_languages:
                r_ids = eng_reading_ids[3:9] if lang == "English" else nep_reading_ids[3:9]
                res = sa.reading_analysis(df_filtered, r_ids, total_words[lang], lang=lang, printText=False)
                comp_read_data.append({
                    "Language": lang,
                    "Percentage": res["analysis_four"]["percentage_meeting"],
                    "Students": res["analysis_four"]["total_students"]
                })
            if comp_read_data:
                df_read_comp = pd.DataFrame(comp_read_data)
                fig = px.bar(
                    df_read_comp, x="Language", y="Percentage", text="Percentage",
                    title="Foundational Reading by Language",
                    color="Percentage", color_continuous_scale="Blues"
                )
                fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                st.plotly_chart(fig, use_container_width=True)