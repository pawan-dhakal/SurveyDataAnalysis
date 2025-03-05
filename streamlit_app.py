#streamlit_app.py
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
# SIDEBAR SCHOOL SELECTION
# -------------------------
st.sidebar.header("School Selection")

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
# OVERVIEW TAB: Enhanced visual summary
# -------------------------
with tab_overview:
    st.header("Survey Data Overview")
    
    # Summary metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Students", len(df_filtered))
    with col2:
        st.metric("Schools Represented", len(df_filtered['school'].unique()))
    
    # Competency comparison with enhanced visualization
    st.subheader("Foundational Competency Comparison")
    
    # Prepare data
    competency_data = []
    for school in df_filtered['school'].unique():
        school_df = df_filtered[df_filtered['school'] == school]
        
        # Numeracy analysis
        numeracy = sa.numeracy_analysis(school_df, sa.numeracy_ids, printText=False)
        # English reading analysis
        eng_reading = sa.reading_analysis(school_df, sa.long_eng_reading_ids, 
                                        sa.total_long_eng_words, "English", printText=False)
        # Nepali reading analysis
        nep_reading = sa.reading_analysis(school_df, sa.long_nep_reading_ids,
                                        sa.total_long_nep_words, "Nepali", printText=False)
        
        competency_data.append({
            "School": school,
            "Numeracy (%)": numeracy['analysis_five']['percentage_meeting'],
            "English Reading (%)": eng_reading['analysis_four']['percentage_meeting'],
            "Nepali Reading (%)": nep_reading['analysis_four']['percentage_meeting']
        })
    
    # Create interactive parallel coordinates plot
    if competency_data:
        df_competency = pd.DataFrame(competency_data)
        fig = px.parallel_coordinates(df_competency,
                                    color="Numeracy (%)",
                                    dimensions=["Numeracy (%)", 
                                               "English Reading (%)", 
                                               "Nepali Reading (%)"],
                                    labels={"Numeracy (%)": "Numeracy<br>%",
                                           "English Reading (%)": "English Reading<br>%",
                                           "Nepali Reading (%)": "Nepali Reading<br>%"},
                                    color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown by competency
    st.subheader("Detailed Competency Breakdown")
    
    # Prepare data for faceted bar chart
    breakdown_data = []
    for school in df_filtered['school'].unique():
        school_df = df_filtered[df_filtered['school'] == school]
        
        # Numeracy breakdown
        numeracy = sa.numeracy_analysis(school_df, sa.numeracy_ids, printText=False)
        breakdown_data.append({
            "School": school,
            "Competency": "Numeracy",
            "Percentage": numeracy['analysis_five']['percentage_meeting']
        })
        
        # English Reading breakdown
        eng_reading = sa.reading_analysis(school_df, sa.long_eng_reading_ids,
                                        sa.total_long_eng_words, "English", printText=False)
        breakdown_data.append({
            "School": school,
            "Competency": "English Reading",
            "Percentage": eng_reading['analysis_four']['percentage_meeting']
        })
        
        # Nepali Reading breakdown
        nep_reading = sa.reading_analysis(school_df, sa.long_nep_reading_ids,
                                        sa.total_long_nep_words, "Nepali", printText=False)
        breakdown_data.append({
            "School": school,
            "Competency": "Nepali Reading",
            "Percentage": nep_reading['analysis_four']['percentage_meeting']
        })
    
    # Create faceted bar chart
    if breakdown_data:
        df_breakdown = pd.DataFrame(breakdown_data)
        fig = px.bar(df_breakdown, x="School", y="Percentage", color="Competency",
                    facet_col="Competency", facet_col_spacing=0.1,
                    height=400, text_auto=".1f",
                    labels={"Percentage": "Achievement Percentage (%)"},
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(showlegend=False)
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# NUMERACY TAB (remains largely the same)
# -------------------------
with tab_numeracy:
    st.header("Numeracy Skills Analysis")
    
    numeracy_analysis = sa.numeracy_analysis(df_filtered, sa.numeracy_ids)
    plots = sa.plot_numeracy_results(numeracy_analysis)
    
    st.subheader("Task Completion Rates")
    st.plotly_chart(plots['fig_overall'], use_container_width=True)
    
    st.subheader("Performance by Gender")
    st.plotly_chart(plots['fig_gender'], use_container_width=True)
    
    if plots['fig_age']:
        st.subheader("Age-wise Progression")
        st.plotly_chart(plots['fig_age'], use_container_width=True)
    
    if plots['fig_grade']:
        st.subheader("Grade-level Performance")
        st.plotly_chart(plots['fig_grade'], use_container_width=True)

# -------------------------
# READING TAB: Separate Sub-Tabs for English & Nepali
# -------------------------
with tab_reading:
    st.header("Reading Proficiency Analysis")
    
    tab_eng, tab_nep = st.tabs([
        "📖 English Reading Analysis", 
        "📖 Nepali Reading Analysis"
    ])
    
    # --- English Reading Analysis ---
    with tab_eng:
        st.subheader("English Reading Analysis")
        
        # Run reading analysis for English
        eng_res = sa.reading_analysis(df_filtered, sa.long_eng_reading_ids, lang="English")
        
        # Overall reading performance plot
        tasks = ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]
        overall_percentages = [
            eng_res['analysis_one']['percentage_meeting'],
            eng_res['analysis_two']['percentage_meeting'],
            eng_res['analysis_three']['percentage_meeting'],
            eng_res['analysis_four']['percentage_meeting']
        ]
        overall_df = pd.DataFrame({"Task": tasks, "Percentage": overall_percentages})
        fig_overall_read = px.bar(
            overall_df, x="Task", y="Percentage", 
            title="Overall English Reading Task Completion",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage"
        )
        fig_overall_read.update_traces(texttemplate='%{text:.1f}%%', textposition='outside')
        st.plotly_chart(fig_overall_read, use_container_width=True)
        
        # Gender breakdown plot for reading tasks
        gender_rows = []
        for gender, metrics in eng_res["analysis_gender"].items():
            for key, label in zip(["read_words", "literal", "inferential", "foundational"],
                                  ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
                gender_rows.append({"Gender": gender, "Task": label, "Percentage": metrics[key]})
        gender_df = pd.DataFrame(gender_rows)
        fig_gender_read = px.bar(
            gender_df, x="Task", y="Percentage", color="Gender",
            title="English Reading Task Completion by Gender",
            barmode="group",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage"
        )
        fig_gender_read.update_traces(texttemplate='%{text:.1f}%%', textposition='outside')
        st.plotly_chart(fig_gender_read, use_container_width=True)
        
        # Grade breakdown plot for reading tasks (English)
        grade_rows = []
        grade_breakdown = eng_res.get("analysis_grade", {})
        for task_key, task_label in zip(["read_words", "literal", "inferential", "foundational"],
                                        ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
            if task_key in grade_breakdown:
                for grade_group, data in grade_breakdown[task_key].items():
                    grade_rows.append({"Grade": grade_group, "Task": task_label, "Percentage": data["percentage"]})
        grade_df = pd.DataFrame(grade_rows)
        fig_grade_read = px.bar(
            grade_df, x="Task", y="Percentage", color="Grade",
            title="English Reading Task Completion by Grade",
            barmode="group",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage"
        )
        fig_grade_read.update_traces(texttemplate='%{text:.1f}%%', textposition='outside')
        st.plotly_chart(fig_grade_read, use_container_width=True)
        
        # Age breakdown plot for reading tasks (English)
        age_rows = []
        age_breakdown = eng_res.get("analysis_age", {})
        for task_key, task_label in zip(["read_words", "literal", "inferential", "foundational"],
                                        ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
            if task_key in age_breakdown:
                for age_group, data in age_breakdown[task_key].items():
                    age_rows.append({"Age": age_group, "Task": task_label, "Percentage": data["percentage"]})
        if age_rows:
            age_df = pd.DataFrame(age_rows)
            fig_age_read = px.line(
                age_df, x="Age", y="Percentage", color="Task",
                title="English Reading Task Completion by Age",
                markers=True,
                labels={"Percentage": "Percentage of Students"}
            )
            st.plotly_chart(fig_age_read, use_container_width=True)
    
    # --- Nepali Reading Analysis ---
    with tab_nep:
        st.subheader("Nepali Reading Analysis")
        
        # Run reading analysis for Nepali
        nep_res = sa.reading_analysis(df_filtered, sa.long_nep_reading_ids, lang="Nepali")
        
        # Overall reading performance plot
        tasks = ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]
        overall_percentages = [
            nep_res['analysis_one']['percentage_meeting'],
            nep_res['analysis_two']['percentage_meeting'],
            nep_res['analysis_three']['percentage_meeting'],
            nep_res['analysis_four']['percentage_meeting']
        ]
        overall_df = pd.DataFrame({"Task": tasks, "Percentage": overall_percentages})
        fig_overall_read = px.bar(
            overall_df, x="Task", y="Percentage", 
            title="Overall Nepali Reading Task Completion",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage"
        )
        fig_overall_read.update_traces(texttemplate='%{text:.1f}%%', textposition='outside')
        st.plotly_chart(fig_overall_read, use_container_width=True)
        
        # Gender breakdown plot for reading tasks
        gender_rows = []
        for gender, metrics in nep_res["analysis_gender"].items():
            for key, label in zip(["read_words", "literal", "inferential", "foundational"],
                                  ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
                gender_rows.append({"Gender": gender, "Task": label, "Percentage": metrics[key]})
        gender_df = pd.DataFrame(gender_rows)
        fig_gender_read = px.bar(
            gender_df, x="Task", y="Percentage", color="Gender",
            title="Nepali Reading Task Completion by Gender",
            barmode="group",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage"
        )
        fig_gender_read.update_traces(texttemplate='%{text:.1f}%%', textposition='outside')
        st.plotly_chart(fig_gender_read, use_container_width=True)
        
        # Grade breakdown plot for reading tasks (Nepali)
        grade_rows = []
        grade_breakdown = nep_res.get("analysis_grade", {})
        for task_key, task_label in zip(["read_words", "literal", "inferential", "foundational"],
                                        ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
            if task_key in grade_breakdown:
                for grade_group, data in grade_breakdown[task_key].items():
                    grade_rows.append({"Grade": grade_group, "Task": task_label, "Percentage": data["percentage"]})
        grade_df = pd.DataFrame(grade_rows)
        fig_grade_read = px.bar(
            grade_df, x="Task", y="Percentage", color="Grade",
            title="Nepali Reading Task Completion by Grade",
            barmode="group",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage"
        )
        fig_grade_read.update_traces(texttemplate='%{text:.1f}%%', textposition='outside')
        st.plotly_chart(fig_grade_read, use_container_width=True)
        
        # Age breakdown plot for reading tasks (Nepali)
        age_rows = []
        age_breakdown = nep_res.get("analysis_age", {})
        for task_key, task_label in zip(["read_words", "literal", "inferential", "foundational"],
                                        ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
            if task_key in age_breakdown:
                for age_group, data in age_breakdown[task_key].items():
                    age_rows.append({"Age": age_group, "Task": task_label, "Percentage": data["percentage"]})
        if age_rows:
            age_df = pd.DataFrame(age_rows)
            fig_age_read = px.line(
                age_df, x="Age", y="Percentage", color="Task",
                title="Nepali Reading Task Completion by Age",
                markers=True,
                labels={"Percentage": "Percentage of Students"}
            )
            st.plotly_chart(fig_age_read, use_container_width=True)

# -------------------------
# GLOBAL STYLE IMPROVEMENTS
# -------------------------
st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
[data-testid="stMetricLabel"] {
    color: #6c757d;
    font-weight: 500;
}
[data-testid="stMetricValue"] {
    color: #2c3e50;
    font-size: 1.8rem !important;
    font-weight: 700;
}
.stPlotlyChart {
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)
