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

    
    # School performance comparison for all schools
    st.subheader("Overall School Comparison")
    school_list = sorted(df_filtered['school'].unique().tolist())
    school_summary = []
    for school in school_list:
        school_df = df_filtered[df_filtered['school'] == school]
        numeracy_res = sa.numeracy_analysis(school_df, sa.numeracy_ids)
        eng_res = sa.reading_analysis(
            school_df, sa.long_eng_reading_ids, sa.total_long_eng_words, "English")
        nep_res = sa.reading_analysis(
            school_df, sa.long_nep_reading_ids, sa.total_long_nep_words, "Nepali")

        school_summary.append({
            "School": school,
            "Numeracy (%)": numeracy_res['analysis_five']['percentage_meeting'],
            "English Reading (%)": eng_res['analysis_four']['percentage_meeting'],
            "Nepali Reading (%)": nep_res['analysis_four']['percentage_meeting']
        })

    summary_df = pd.DataFrame(school_summary)
    fig_summary = px.bar(
        summary_df,
        x="School",
        y=["Numeracy (%)", "English Reading (%)", "Nepali Reading (%)"],
        barmode="group",
        title="Competency Comparison Across Schools"
    )
    fig_summary.update_traces(textposition='outside')
    st.plotly_chart(fig_summary, use_container_width=True)

    st.markdown("---")
    st.subheader("Population Breakdown")
    row1_col1, row1_col2 = st.columns([2, 3])
    with row1_col1:
        gender_counts = df_filtered['studentGender'].value_counts()
        fig_gender = px.pie(
            gender_counts,
            values=gender_counts.values,
            names=gender_counts.index,
            title="Gender Distribution",
            hole=0.4
        )
        st.plotly_chart(fig_gender, use_container_width=True)
    with row1_col2:
        grade_counts = df_filtered['grade'].value_counts().sort_index()
        fig_grade = px.bar(
            grade_counts,
            x=grade_counts.index,
            y=grade_counts.values,
            labels={'x': 'Grade', 'y': 'Number of Students'},
            title="Grade Distribution"
        )
        st.plotly_chart(fig_grade, use_container_width=True)

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
        eng_res = sa.reading_analysis(
            df_filtered, sa.long_eng_reading_ids, lang="English")

        # Total students (used for overall count calculations)
        total_students = len(df_filtered)

        # Overall reading performance plot
        tasks = ["Reading (Words)", "Literal Comprehension",
                 "Inferential Comprehension", "Foundational Reading"]
        overall_percentages = [
            eng_res['analysis_one']['percentage_meeting'],
            eng_res['analysis_two']['percentage_meeting'],
            eng_res['analysis_three']['percentage_meeting'],
            eng_res['analysis_four']['percentage_meeting']
        ]
        # Compute count as a simple approximation (adjust if your analysis returns counts)
        overall_counts = [round(p * total_students / 100) for p in overall_percentages]

        overall_df = pd.DataFrame({
            "Task": tasks,
            "Percentage": overall_percentages,
            "Count": overall_counts
        })
        fig_overall_read = px.bar(
            overall_df, x="Task", y="Percentage",
            title="Overall English Reading Task Completion",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage",
            # Show count and formatted percentage in tooltip
            hover_data={"Count": True, "Percentage": ':.1f'}
        )
        fig_overall_read.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_overall_read, use_container_width=True)

        # Gender breakdown plot for reading tasks
        # Compute totals for each gender from the filtered dataframe
        gender_totals = df_filtered['studentGender'].value_counts().to_dict()
        gender_rows = []
        for gender, metrics in eng_res["analysis_gender"].items():
            for key, label in zip(["read_words", "literal", "inferential", "foundational"],
                                  ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
                total_gender = gender_totals.get(gender, 0)
                count = round(metrics[key] * total_gender / 100)
                gender_rows.append({
                    "Gender": gender,
                    "Task": label,
                    "Percentage": metrics[key],
                    "Count": count
                })
        gender_df = pd.DataFrame(gender_rows)
        fig_gender_read = px.bar(
            gender_df, x="Task", y="Percentage", color="Gender",
            title="English Reading Task Completion by Gender",
            barmode="group",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage",
            hover_data={"Count": True}
        )
        fig_gender_read.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_gender_read, use_container_width=True)

        # Grade breakdown plot for reading tasks (English)
        grade_totals = df_filtered['grade'].value_counts().to_dict()
        grade_rows = []
        grade_breakdown = eng_res.get("analysis_grade", {})
        for task_key, task_label in zip(["read_words", "literal", "inferential", "foundational"],
                                        ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
            if task_key in grade_breakdown:
                for grade_group, data in grade_breakdown[task_key].items():
                    total_grade = grade_totals.get(grade_group, 0)
                    count = round(data["percentage"] * total_grade / 100)
                    grade_rows.append({
                        "Grade": grade_group,
                        "Task": task_label,
                        "Percentage": data["percentage"],
                        "Count": count
                    })
        grade_df = pd.DataFrame(grade_rows)
        fig_grade_read = px.bar(
            grade_df, x="Task", y="Percentage", color="Grade",
            title="English Reading Task Completion by Grade",
            barmode="group",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage",
            hover_data={"Count": True}
        )
        fig_grade_read.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_grade_read, use_container_width=True)

        # Age breakdown plot for reading tasks (English)
        # If an 'age' column exists, compute age totals; otherwise adjust as needed.
        if 'age' in df_filtered.columns:
            age_totals = df_filtered['age'].value_counts().to_dict()
        else:
            age_totals = {}
        age_rows = []
        age_breakdown = eng_res.get("analysis_age", {})
        for task_key, task_label in zip(["read_words", "literal", "inferential", "foundational"],
                                        ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
            if task_key in age_breakdown:
                for age_group, data in age_breakdown[task_key].items():
                    total_age = age_totals.get(age_group, 0)
                    count = round(data["percentage"] * total_age / 100) if total_age else 0
                    age_rows.append({
                        "Age": age_group,
                        "Task": task_label,
                        "Percentage": data["percentage"],
                        "Count": count
                    })
        if age_rows:
            age_df = pd.DataFrame(age_rows)
            fig_age_read = px.line(
                age_df, x="Age", y="Percentage", color="Task",
                title="English Reading Task Completion by Age",
                markers=True,
                labels={"Percentage": "Percentage of Students"},
                hover_data={"Count": True}
            )
            st.plotly_chart(fig_age_read, use_container_width=True)

    # --- Nepali Reading Analysis ---
    with tab_nep:
        st.subheader("Nepali Reading Analysis")

        # Run reading analysis for Nepali
        nep_res = sa.reading_analysis(
            df_filtered, sa.long_nep_reading_ids, lang="Nepali")

        # Overall reading performance plot for Nepali
        overall_percentages = [
            nep_res['analysis_one']['percentage_meeting'],
            nep_res['analysis_two']['percentage_meeting'],
            nep_res['analysis_three']['percentage_meeting'],
            nep_res['analysis_four']['percentage_meeting']
        ]
        overall_counts = [round(p * total_students / 100) for p in overall_percentages]

        overall_df = pd.DataFrame({
            "Task": tasks,
            "Percentage": overall_percentages,
            "Count": overall_counts
        })
        fig_overall_read = px.bar(
            overall_df, x="Task", y="Percentage",
            title="Overall Nepali Reading Task Completion",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage",
            hover_data={"Count": True, "Percentage": ':.1f'}
        )
        fig_overall_read.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_overall_read, use_container_width=True)

        # Gender breakdown plot for Nepali reading tasks
        gender_rows = []
        for gender, metrics in nep_res["analysis_gender"].items():
            for key, label in zip(["read_words", "literal", "inferential", "foundational"],
                                  ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
                total_gender = gender_totals.get(gender, 0)
                count = round(metrics[key] * total_gender / 100)
                gender_rows.append({
                    "Gender": gender,
                    "Task": label,
                    "Percentage": metrics[key],
                    "Count": count
                })
        gender_df = pd.DataFrame(gender_rows)
        fig_gender_read = px.bar(
            gender_df, x="Task", y="Percentage", color="Gender",
            title="Nepali Reading Task Completion by Gender",
            barmode="group",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage",
            hover_data={"Count": True}
        )
        fig_gender_read.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_gender_read, use_container_width=True)

        # Grade breakdown plot for Nepali reading tasks
        grade_rows = []
        grade_breakdown = nep_res.get("analysis_grade", {})
        for task_key, task_label in zip(["read_words", "literal", "inferential", "foundational"],
                                        ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
            if task_key in grade_breakdown:
                for grade_group, data in grade_breakdown[task_key].items():
                    total_grade = grade_totals.get(grade_group, 0)
                    count = round(data["percentage"] * total_grade / 100)
                    grade_rows.append({
                        "Grade": grade_group,
                        "Task": task_label,
                        "Percentage": data["percentage"],
                        "Count": count
                    })
        grade_df = pd.DataFrame(grade_rows)
        fig_grade_read = px.bar(
            grade_df, x="Task", y="Percentage", color="Grade",
            title="Nepali Reading Task Completion by Grade",
            barmode="group",
            labels={"Percentage": "Percentage of Students"},
            text="Percentage",
            hover_data={"Count": True}
        )
        fig_grade_read.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_grade_read, use_container_width=True)

        # Age breakdown plot for Nepali reading tasks
        age_rows = []
        age_breakdown = nep_res.get("analysis_age", {})
        for task_key, task_label in zip(["read_words", "literal", "inferential", "foundational"],
                                        ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]):
            if task_key in age_breakdown:
                for age_group, data in age_breakdown[task_key].items():
                    total_age = age_totals.get(age_group, 0)
                    count = round(data["percentage"] * total_age / 100) if total_age else 0
                    age_rows.append({
                        "Age": age_group,
                        "Task": task_label,
                        "Percentage": data["percentage"],
                        "Count": count
                    })
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
