#survey_analysis.py
import os
import pandas as pd
import plotly.express as px

def load_data(filepath):
    """
    Load the CSV file into a pandas DataFrame and clean the data.
    """
    df = pd.read_csv(filepath)
    df = clean_data(df)
    return df

def clean_data(df):
    """
    Clean the DataFrame by converting columns to the correct types and 
    dropping rows with missing essential information.
    """
    # Convert studentAge to numeric and drop rows where it is missing.
    df['studentAge'] = pd.to_numeric(df['studentAge'], errors='coerce')
    df = df.dropna(subset=['studentAge'])
    
    # Drop rows missing other key columns (grade, studentGender, school).
    for col in ['grade', 'studentGender', 'school']:
        if col in df.columns:
            df = df.dropna(subset=[col])
    return df

# ---------------------------
# Numeracy Analysis Functions
# ---------------------------
def numeracy_analysis(df, ids, school=None, printText=True):
    """
    Perform numeracy analysis on the provided DataFrame.
    Returns breakdowns by overall performance, gender, age, and grade.
    """
    if school is not None and school.lower() != "all":
        df = df[df['school'] == school]
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    total_students = df.shape[0]
    genders = df['studentGender'].unique()
    
    # Define groups of question IDs
    number_reading_qIDs = [ids[i] for i in [0, 1, 2, 3, 4, 5]]
    number_discrim_qIDs = [ids[i] for i in [6, 7, 8, 9, 10]]
    addition_qIDs = [ids[i] for i in [11, 12, 13, 14, 15]]
    pattern_recog_qIDs = [ids[i] for i in [18, 19, 20, 21]]

    
    
    # Conditions for correct responses
    condition_reading = (df[number_reading_qIDs] == 'Correct').all(axis=1)
    condition_discrimination = (df[number_discrim_qIDs] == 'Correct').all(axis=1)
    condition_addition = (df[addition_qIDs] == 'Correct').all(axis=1)
    condition_pattern = (df[pattern_recog_qIDs] == 'Correct').all(axis=1)
    condition_all = condition_reading & condition_discrimination & condition_addition & condition_pattern

    def calculate_percentage_and_gender_results(condition):
        df_meeting = df[condition]
        count_meeting = df_meeting.shape[0]
        percentage_meeting = (count_meeting / total_students) * 100 if total_students else 0
        
        gender_results = {}
        for gender in genders:
            df_gender = df[df['studentGender'] == gender]
            total_gender = df_gender.shape[0]
            # For gender breakdown, we use the reading task condition as an example.
            gender_condition = (df_gender[number_reading_qIDs] == 'Correct').all(axis=1)
            count_gender = df_gender[gender_condition].shape[0]
            percentage_gender = (count_gender / total_gender) * 100 if total_gender else 0
            gender_results[gender] = {
                "total_students": total_gender,
                "count": count_gender,
                "percentage": percentage_gender
            }
        return {
            "total_students": total_students,
            "count_meeting": count_meeting,
            "percentage_meeting": percentage_meeting,
            "gender_results": gender_results
        }
    
    def calculate_percentage_by_group(condition, group_by_col):
        grouped = df.groupby(group_by_col)
        percentage_results = {}
        for group, group_df in grouped:
            count_meeting = condition[group_df.index].sum()
            total_group = group_df.shape[0]
            perc = (count_meeting / total_group) * 100 if total_group > 0 else 0
            percentage_results[group] = {
                "count_meeting": count_meeting,
                "total_students": total_group,
                "percentage": perc
            }
        return percentage_results

    def analysis_one():
        return calculate_percentage_and_gender_results(condition_reading)

    def analysis_two():
        return calculate_percentage_and_gender_results(condition_discrimination)

    def analysis_three():
        return calculate_percentage_and_gender_results(condition_addition)

    def analysis_four():
        return calculate_percentage_and_gender_results(condition_pattern)

    def analysis_five():
        return calculate_percentage_and_gender_results(condition_all)

    def analysis_age():
        return {
            "number_reading": calculate_percentage_by_group(condition_reading, 'studentAge'),
            "number_discrimination": calculate_percentage_by_group(condition_discrimination, 'studentAge'),
            "addition": calculate_percentage_by_group(condition_addition, 'studentAge'),
            "pattern_recognition": calculate_percentage_by_group(condition_pattern, 'studentAge'),
            "foundational_numeracy": calculate_percentage_by_group(condition_all, 'studentAge')
        }

    def analysis_grade():
        return {
            "number_reading": calculate_percentage_by_group(condition_reading, 'grade'),
            "number_discrimination": calculate_percentage_by_group(condition_discrimination, 'grade'),
            "addition": calculate_percentage_by_group(condition_addition, 'grade'),
            "pattern_recognition": calculate_percentage_by_group(condition_pattern, 'grade'),
            "foundational_numeracy": calculate_percentage_by_group(condition_all, 'grade')
        }
    
    analysis_results = {
        "analysis_one": analysis_one(),
        "analysis_two": analysis_two(),
        "analysis_three": analysis_three(),
        "analysis_four": analysis_four(),
        "analysis_five": analysis_five(),
        "analysis_age": analysis_age(),
        "analysis_grade": analysis_grade()
    }
    
    if printText:
        print("Numeracy analysis complete.")
    
    return analysis_results

# ---------------------------
# Reading Analysis Functions
# ---------------------------
def reading_analysis(df, ids, total_words, lang="English", school=None, printText=True):
    """
    Perform reading analysis on the provided DataFrame.
    Returns breakdowns by overall performance, gender, age, and grade.
    """
    if school is not None and school.lower() != "all":
        df = df[df['school'] == school]
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    total_students = df.shape[0]
    genders = df['studentGender'].unique()
    
    required_correct_words = int(0.9 * total_words)  # 90% threshold
    qID = ids[0]
    df[qID] = pd.to_numeric(df[qID], errors='coerce')
    df = df.dropna(subset=[qID])
    
    # Define question groups for comprehension
    lit_comp_qIDs = [ids[i] for i in [0, 1, 2, 3]]
    inf_comp_qIDs = [ids[i] for i in [0, 4, 5]]
    
    condition_reading_story = df[qID] >= required_correct_words
    condition_lit_comp = (df[qID] >= required_correct_words) & \
                         (df[lit_comp_qIDs[1]] == 'Correct') & \
                         (df[lit_comp_qIDs[2]] == 'Correct') & \
                         (df[lit_comp_qIDs[3]] == 'Correct')
    condition_inf_comp = (df[qID] >= required_correct_words) & \
                         (df[inf_comp_qIDs[1]].astype(str) == 'Correct') & \
                         (df[inf_comp_qIDs[2]].astype(str) == 'Correct')
    condition_all = condition_reading_story & condition_lit_comp & condition_inf_comp
    
    def calculate_percentage_by_group(condition, group_by_col):
        grouped = df.groupby(group_by_col)
        results = {}
        for group, group_df in grouped:
            count_meeting = condition[group_df.index].sum()
            total_group = group_df.shape[0]
            perc = (count_meeting / total_group) * 100 if total_group > 0 else 0
            results[group] = {"count": count_meeting, "total": total_group, "percentage": perc}
        return results

    def analysis_one():
        df_meeting = df[condition_reading_story]
        count_meeting = df_meeting.shape[0]
        percentage_meeting = (count_meeting / total_students) * 100 if total_students else 0
        gender_results = {}
        for gender in genders:
            df_gender = df[df['studentGender'] == gender]
            total_gender = df_gender.shape[0]
            gender_condition = df_gender[qID] >= required_correct_words
            count_gender = df_gender[gender_condition].shape[0]
            percentage_gender = (count_gender / total_gender) * 100 if total_gender else 0
            gender_results[gender] = {
                "total_students": total_gender,
                "count": count_gender,
                "percentage": percentage_gender
            }
        return {
            "total_students": total_students,
            "count_meeting": count_meeting,
            "percentage_meeting": percentage_meeting,
            "gender_results": gender_results
        }
    
    def analysis_two():
        df_meeting = df[condition_lit_comp]
        count_meeting = df_meeting.shape[0]
        percentage_meeting = (count_meeting / total_students) * 100 if total_students else 0
        return {"total_students": total_students, "count_meeting": count_meeting, "percentage_meeting": percentage_meeting}
    
    def analysis_three():
        df_meeting = df[condition_inf_comp]
        count_meeting = df_meeting.shape[0]
        percentage_meeting = (count_meeting / total_students) * 100 if total_students else 0
        return {"total_students": total_students, "count_meeting": count_meeting, "percentage_meeting": percentage_meeting}
    
    def analysis_four():
        df_meeting = df[condition_all]
        count_meeting = df_meeting.shape[0]
        percentage_meeting = (count_meeting / total_students) * 100 if total_students else 0
        return {"total_students": total_students, "count_meeting": count_meeting, "percentage_meeting": percentage_meeting}
    
    def analysis_age():
        return {
            "read_words": calculate_percentage_by_group(condition_reading_story, 'studentAge'),
            "literal": calculate_percentage_by_group(condition_lit_comp, 'studentAge'),
            "inferential": calculate_percentage_by_group(condition_inf_comp, 'studentAge'),
            "foundational": calculate_percentage_by_group(condition_all, 'studentAge')
        }
    
    def analysis_gender():
        results = {}
        for gender in genders:
            sub_df = df[df['studentGender'] == gender]
            total_gender = sub_df.shape[0]
            if total_gender > 0:
                results[gender] = {
                    "read_words": (sub_df[qID] >= required_correct_words).sum() / total_gender * 100,
                    "literal": (((sub_df[qID] >= required_correct_words) & 
                                 (sub_df[lit_comp_qIDs[1]] == 'Correct') & 
                                 (sub_df[lit_comp_qIDs[2]] == 'Correct') & 
                                 (sub_df[lit_comp_qIDs[3]] == 'Correct')).sum() / total_gender * 100),
                    "inferential": (((sub_df[qID] >= required_correct_words) & 
                                     (sub_df[inf_comp_qIDs[1]].astype(str) == 'Correct') & 
                                     (sub_df[inf_comp_qIDs[2]].astype(str) == 'Correct')).sum() / total_gender * 100),
                    "foundational": (((sub_df[qID] >= required_correct_words) & 
                                      (sub_df[lit_comp_qIDs[1]] == 'Correct') & 
                                      (sub_df[lit_comp_qIDs[2]] == 'Correct') & 
                                      (sub_df[lit_comp_qIDs[3]] == 'Correct') &
                                      (sub_df[inf_comp_qIDs[1]].astype(str) == 'Correct') & 
                                      (sub_df[inf_comp_qIDs[2]].astype(str) == 'Correct')).sum() / total_gender * 100)
                }
        return results
    
    def analysis_grade():
        return {
            "read_words": calculate_percentage_by_group(condition_reading_story, 'grade'),
            "literal": calculate_percentage_by_group(condition_lit_comp, 'grade'),
            "inferential": calculate_percentage_by_group(condition_inf_comp, 'grade'),
            "foundational": calculate_percentage_by_group(condition_all, 'grade')
        }
    
    analysis_results = {
        "analysis_one": analysis_one(),
        "analysis_two": analysis_two(),
        "analysis_three": analysis_three(),
        "analysis_four": analysis_four(),
        "analysis_age": analysis_age(),
        "analysis_gender": analysis_gender(),
        "analysis_grade": analysis_grade()
    }
    
    if printText:
        print("Reading analysis (lang=%s) complete." % lang)
    
    return analysis_results

# ---------------------------
# Plotting Functions (with improved styling)
# ---------------------------
def plot_numeracy_results(analysis_results):
    """
    Create Plotly figures for numeracy analysis results with improved styling.
    """
    task_labels = ['Number Reading', 'Number Discrimination', 'Addition', 'Pattern Recognition', 'Foundational Numeracy']
    overall_data = [
        analysis_results['analysis_one']['percentage_meeting'],
        analysis_results['analysis_two']['percentage_meeting'],
        analysis_results['analysis_three']['percentage_meeting'],
        analysis_results['analysis_four']['percentage_meeting'],
        analysis_results['analysis_five']['percentage_meeting']
    ]
    
    gender_data = {
        'Male': [
            analysis_results['analysis_one']['gender_results'].get('Male', {}).get('percentage', 0),
            analysis_results['analysis_two']['gender_results'].get('Male', {}).get('percentage', 0),
            analysis_results['analysis_three']['gender_results'].get('Male', {}).get('percentage', 0),
            analysis_results['analysis_four']['gender_results'].get('Male', {}).get('percentage', 0),
            analysis_results['analysis_five']['gender_results'].get('Male', {}).get('percentage', 0)
        ],
        'Female': [
            analysis_results['analysis_one']['gender_results'].get('Female', {}).get('percentage', 0),
            analysis_results['analysis_two']['gender_results'].get('Female', {}).get('percentage', 0),
            analysis_results['analysis_three']['gender_results'].get('Female', {}).get('percentage', 0),
            analysis_results['analysis_four']['gender_results'].get('Female', {}).get('percentage', 0),
            analysis_results['analysis_five']['gender_results'].get('Female', {}).get('percentage', 0)
        ]
    }
    
    overall_df = pd.DataFrame({
        'Task': task_labels,
        'Percentage': overall_data
    })
    
    fig_overall = px.bar(overall_df, x='Task', y='Percentage', 
                         title="Overall Numeracy Task Completion Percentage",
                         labels={'Percentage': 'Percentage of Students'},
                         text='Percentage')
    fig_overall.update_layout(
        yaxis=dict(range=[0, 120], tickformat=".2f"),
        showlegend=False,
        autosize=True,
        margin=dict(l=10, r=10, t=40, b=10),
        template='plotly_white'
    )
    fig_overall.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    
    gender_df = pd.DataFrame({
        'Task': task_labels * 2,
        'Percentage': gender_data['Male'] + gender_data['Female'],
        'Gender': ['Male'] * 5 + ['Female'] * 5
    })
    
    fig_gender = px.bar(gender_df, x='Task', y='Percentage', color='Gender',
                        title="Numeracy Task Completion by Gender",
                        barmode='group', text='Percentage',
                        labels={'Percentage': 'Percentage of Students'})
    fig_gender.update_layout(
        yaxis=dict(range=[0, 120], tickformat=".2f"),
        autosize=True,
        margin=dict(l=10, r=10, t=40, b=10),
        template='plotly_white'
    )
    fig_gender.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    
    # Age-wise analysis
    age_analysis = analysis_results.get('analysis_age', {})
    age_data = {'Age': [], 'Percentage': [], 'Task': []}
    mapping = {
        'Number Reading': 'number_reading',
        'Number Discrimination': 'number_discrimination',
        'Addition': 'addition',
        'Pattern Recognition': 'pattern_recognition',
        'Foundational Numeracy': 'foundational_numeracy'
    }
    for task in task_labels:
        task_key = mapping.get(task)
        if task_key in age_analysis:
            for age_group, data in age_analysis[task_key].items():
                age_data['Age'].append(age_group)
                age_data['Percentage'].append(data['percentage'])
                age_data['Task'].append(task)
    age_fig = None
    if age_data['Age']:
        age_df = pd.DataFrame(age_data)
        age_fig = px.line(age_df, x='Age', y='Percentage', color='Task',
                          title="Numeracy Task Completion by Age",
                          markers=True,
                          labels={'Percentage': 'Percentage of Students'})
        age_fig.update_layout(
            yaxis=dict(range=[0, 140], tickformat=".2f"),
            xaxis_title="Age (years)",
            yaxis_title="Percentage of Students",
            autosize=True,
            margin=dict(l=10, r=10, t=40, b=10),
            template='plotly_white'
        )
    
    # Grade-wise analysis
    grade_analysis = analysis_results.get('analysis_grade', {})
    grade_data = {'Task': [], 'Percentage': [], 'Grade': []}
    for task in task_labels:
        task_key = mapping.get(task)
        if task_key in grade_analysis:
            for grade_group, data in grade_analysis[task_key].items():
                grade_data['Task'].append(task)
                grade_data['Percentage'].append(data['percentage'])
                grade_data['Grade'].append(grade_group)
    grade_fig = None
    if grade_data['Task']:
        grade_df = pd.DataFrame(grade_data)
        grade_fig = px.bar(grade_df, x='Task', y='Percentage', color='Grade',
                           title="Numeracy Task Completion by Grade",
                           barmode='group', text='Percentage',
                           labels={'Percentage': 'Percentage of Students'})
        grade_fig.update_layout(
            yaxis=dict(range=[0, 120], tickformat=".2f"),
            autosize=True,
            margin=dict(l=10, r=10, t=40, b=10),
            template='plotly_white'
        )
        grade_fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    
    return {
        "fig_overall": fig_overall,
        "fig_gender": fig_gender,
        "fig_age": age_fig,
        "fig_grade": grade_fig
    }

def plot_reading_results(results, lang, school_name):
    """
    Create a Plotly bar chart for reading analysis results with improved styling.
    """
    analysis_titles = [
        "Read 90%+ Words Correctly",
        "Literal Comprehension Correct",
        "Inferential Comprehension Correct",
        "Foundational Skills Demonstrated"
    ]
    percentages = [
        results['analysis_one']['percentage_meeting'],
        results['analysis_two']['percentage_meeting'],
        results['analysis_three']['percentage_meeting'],
        results['analysis_four']['percentage_meeting']
    ]
    plot_data = {
        "Criteria": analysis_titles,
        "Percentage": percentages
    }
    fig = px.bar(plot_data, x="Criteria", y="Percentage", 
                 title=f"{lang} Reading Analysis Results - {school_name}",
                 labels={"Percentage": "Percentage (%)"},
                 text='Percentage',
                 color='Percentage',
                 color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(yaxis=dict(range=[0, 100]),
                      autosize=True,
                      margin=dict(l=10, r=10, t=40, b=10),
                      template='plotly_white')
    return fig

def plot_reading_breakdown(analysis_age, analysis_gender):
    """
    Create additional Plotly figures for reading analysis breakdowns by age and gender.
    """
    # Age breakdown: line chart for each metric by student age.
    age_data = {"Age": [], "Percentage": [], "Metric": []}
    for metric, breakdown in analysis_age.items():
        for age, data in breakdown.items():
            age_data["Age"].append(age)
            age_data["Percentage"].append(data["percentage"])
            age_data["Metric"].append(metric)
    fig_age = None
    if age_data["Age"]:
        age_df = pd.DataFrame(age_data)
        fig_age = px.line(age_df, x="Age", y="Percentage", color="Metric",
                          markers=True, title="Reading Analysis by Age",
                          labels={"Percentage": "Percentage of Students", "Age": "Student Age"})
        fig_age.update_layout(autosize=True,
                              margin=dict(l=10, r=10, t=40, b=10),
                              template='plotly_white')
    
    # Gender breakdown: bar chart for each metric by gender.
    gender_data = {"Gender": [], "Metric": [], "Percentage": []}
    for gender, metrics in analysis_gender.items():
        for metric, percentage in metrics.items():
            gender_data["Gender"].append(gender)
            gender_data["Metric"].append(metric)
            gender_data["Percentage"].append(percentage)
    fig_gender = None
    if gender_data["Gender"]:
        gender_df = pd.DataFrame(gender_data)
        fig_gender = px.bar(gender_df, x="Metric", y="Percentage", color="Gender",
                            barmode='group', title="Reading Analysis by Gender",
                            labels={"Percentage": "Percentage of Students"})
        fig_gender.update_layout(autosize=True,
                                 margin=dict(l=10, r=10, t=40, b=10),
                                 template='plotly_white')
        fig_gender.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    
    return {
        "fig_reading_age": fig_age,
        "fig_reading_gender": fig_gender
    }

# ---------------------------
# Formatted Results Functions
# ---------------------------
def get_formatted_numeracy_results(results):
    """
    Return a formatted multi‐line string of numeracy results.
    """
    lines = []
    lines.append("** Numeracy Analysis Results **")
    lines.append("-" * 40)
    lines.append(f"1. Number Reading Completed: {results['analysis_one']['percentage_meeting']:.2f}% "
                 f"({results['analysis_one']['count_meeting']}/{results['analysis_one']['total_students']})")
    lines.append(f"2. Number Discrimination Completed: {results['analysis_two']['percentage_meeting']:.2f}% "
                 f"({results['analysis_two']['count_meeting']}/{results['analysis_two']['total_students']})")
    lines.append(f"3. Addition Completed: {results['analysis_three']['percentage_meeting']:.2f}% "
                 f"({results['analysis_three']['count_meeting']}/{results['analysis_three']['total_students']})")
    lines.append(f"4. Pattern Recognition Completed: {results['analysis_four']['percentage_meeting']:.2f}% "
                 f"({results['analysis_four']['count_meeting']}/{results['analysis_four']['total_students']})")
    lines.append(f"5. Foundational Numeracy Skills Demonstrated: {results['analysis_five']['percentage_meeting']:.2f}% "
                 f"({results['analysis_five']['count_meeting']}/{results['analysis_five']['total_students']})")
    lines.append("-" * 40)
    return "\n".join(lines)

def get_formatted_reading_results(results, lang):
    """
    Return a formatted multi‐line string of reading results.
    """
    lines = []
    lines.append(f"** {lang} Reading Analysis Results **")
    lines.append("-" * 40)
    lines.append(f"1. Read 90%+ Words Correctly: {results['analysis_one']['percentage_meeting']:.2f}% "
                 f"({results['analysis_one']['count_meeting']}/{results['analysis_one']['total_students']})")
    lines.append(f"2. Literal Comprehension Correct: {results['analysis_two']['percentage_meeting']:.2f}% "
                 f"({results['analysis_two']['count_meeting']}/{results['analysis_two']['total_students']})")
    lines.append(f"3. Inferential Comprehension Correct: {results['analysis_three']['percentage_meeting']:.2f}% "
                 f"({results['analysis_three']['count_meeting']}/{results['analysis_three']['total_students']})")
    lines.append(f"4. Foundational Reading Skills Demonstrated: {results['analysis_four']['percentage_meeting']:.2f}% "
                 f"({results['analysis_four']['count_meeting']}/{results['analysis_four']['total_students']})")
    lines.append("-" * 40)
    return "\n".join(lines)

# ---------------------------
# New Summary Function
# ---------------------------
def foundational_skills_summary(df, reading_ids, numeracy_ids, total_words_read, language="English"):
    """
    Compute summary metrics for foundational reading and numeracy skills.
    Metrics are computed for children aged 7-14 and for those attending grade 2/3.
    Also computes gender parity indices for reading.
    Returns a dictionary with the results.
    """
    # Overall analysis for age 7-14
    df_overall = df[(df['studentAge'] >= 7) & (df['studentAge'] <= 14)]
    reading_res = reading_analysis(df_overall.copy(), reading_ids, total_words_read, lang=language, printText=False)
    numeracy_res = numeracy_analysis(df_overall.copy(), numeracy_ids, printText=False)
    
    summary = {
       "total_records_overall": df_overall.shape[0],
       "reading_foundational_overall": reading_res['analysis_four']['percentage_meeting'],
       "numeracy_foundational_overall": numeracy_res['analysis_five']['percentage_meeting'],
       "reading_gender_parity_overall": reading_res['analysis_one']['gender_results'], 
       "numeracy_gender_parity_overall": numeracy_res['analysis_one']['gender_results']
    }
    
    # Analysis for children attending grade 2/3
    if 'grade' in df.columns:
        df_grade = df[df['grade'].isin(['2', '3', 2, 3])]
        reading_res_grade = reading_analysis(df_grade.copy(), reading_ids, total_words_read, lang=language, printText=False)
        numeracy_res_grade = numeracy_analysis(df_grade.copy(), numeracy_ids, printText=False)
        summary["total_records_grade_2_3"] = df_grade.shape[0]
        summary["reading_foundational_grade"] = reading_res_grade['analysis_four']['percentage_meeting']
        summary["numeracy_foundational_grade"] = numeracy_res_grade['analysis_five']['percentage_meeting']
        summary["reading_gender_parity_grade"] = reading_res_grade['analysis_one']['gender_results']
        summary["numeracy_gender_parity_grade"] = numeracy_res_grade['analysis_one']['gender_results']
    
    return summary
