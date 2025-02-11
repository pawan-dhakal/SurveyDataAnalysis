import os
import pandas as pd
import plotly.express as px

def load_data(filepath):
    """
    Load the CSV file into a pandas DataFrame.
    """
    df = pd.read_csv(filepath)
    return df

def numeracy_analysis(df, ids, school=None, printText=True):
    """
    Perform numeracy analysis on the provided DataFrame.
    
    Parameters:
    - df: DataFrame containing survey records.
    - ids: List of question IDs for the numeracy tasks.
    - school: Optional; if provided (and not "all"), filters the data to that school.
    - printText: If True, prints out additional info.
    
    Returns:
    A dictionary of analysis results.
    """
    # If a specific school is chosen, filter the DataFrame.
    if school is not None and school.lower() != "all":
        df = df[df['school'] == school]
    
    # If the DataFrame has multi-index columns, convert to single-level.
    if isinstance(df.columns, pd.MultiIndex):
        _ = {col[0]: col[1] for col in df.columns}
        df.columns = df.columns.get_level_values(0)
    
    total_students = df.shape[0]
    schools = df['school'].unique()
    genders = df['studentGender'].unique()
    
    # Define groups of question IDs (using the indices as in the original code)
    number_reading_qIDs = [ids[i] for i in [0, 1, 2, 3, 4, 5]]
    number_discrim_qIDs = [ids[i] for i in [6, 7, 8, 9, 10]]
    addition_qIDs = [ids[i] for i in [11, 12, 13, 14, 15]]
    pattern_recog_qIDs = [ids[i] for i in [18, 19, 20, 21]]
    
    # Define conditions for correct responses
    condition_reading = (df[number_reading_qIDs] == 'Correct').all(axis=1)
    condition_discrimination = (df[number_discrim_qIDs] == 'Correct').all(axis=1)
    condition_addition = (df[addition_qIDs] == 'Correct').all(axis=1)
    condition_pattern = (df[pattern_recog_qIDs] == 'Correct').all(axis=1)
    condition_all = condition_reading & condition_discrimination & condition_addition & condition_pattern

    # Helper to calculate overall and gender‐specific percentages
    def calculate_percentage_and_gender_results(condition):
        df_meeting = df[condition]
        count_meeting = df_meeting.shape[0]
        percentage_meeting = (count_meeting / total_students) * 100 if total_students else 0
        
        gender_results = {}
        for gender in genders:
            df_gender = df[df['studentGender'] == gender]
            total_gender = df_gender.shape[0]
            # Note: using the reading condition for gender breakdown (as in your original code)
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
    
    # Helper to calculate percentages by a grouping variable (age or grade)
    def calculate_percentage_by_age_or_grade(condition, group_by_col):
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
            "number_reading": calculate_percentage_by_age_or_grade(condition_reading, 'studentAge'),
            "number_discrimination": calculate_percentage_by_age_or_grade(condition_discrimination, 'studentAge'),
            "addition": calculate_percentage_by_age_or_grade(condition_addition, 'studentAge'),
            "pattern_recognition": calculate_percentage_by_age_or_grade(condition_pattern, 'studentAge'),
            "foundational_numeracy": calculate_percentage_by_age_or_grade(condition_all, 'studentAge')
        }

    def analysis_grade():
        return {
            "number_reading": calculate_percentage_by_age_or_grade(condition_reading, 'grade'),
            "number_discrimination": calculate_percentage_by_age_or_grade(condition_discrimination, 'grade'),
            "addition": calculate_percentage_by_age_or_grade(condition_addition, 'grade'),
            "pattern_recognition": calculate_percentage_by_age_or_grade(condition_pattern, 'grade'),
            "foundational_numeracy": calculate_percentage_by_age_or_grade(condition_all, 'grade')
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
        print("Number reading IDs:", number_reading_qIDs)
        print("Number discrimination IDs:", number_discrim_qIDs)
        print("Addition IDs:", addition_qIDs)
        print("Pattern recognition IDs:", pattern_recog_qIDs)
        print()
    
    return analysis_results

def reading_analysis(df, ids, total_words, lang="English", school=None, printText=True):
    """
    Perform reading analysis on the provided DataFrame.
    
    Parameters:
    - df: DataFrame with survey records.
    - ids: List of question IDs for the reading tasks.
    - total_words: Total word count of the story.
    - lang: Language of the test ("English" or "Nepali").
    - school: Optional; if provided (and not "all"), filters to that school.
    - printText: If True, prints additional info.
    
    Returns:
    A dictionary of analysis results.
    """
    if school is not None and school.lower() != "all":
        df = df[df['school'] == school]
    
    if isinstance(df.columns, pd.MultiIndex):
        _ = {col[0]: col[1] for col in df.columns}
        df.columns = df.columns.get_level_values(0)
    
    total_students = df.shape[0]
    schools = df['school'].unique()
    genders = df['studentGender'].unique()
    
    required_correct_words = int(0.9 * total_words)  # 90% threshold
    qID = ids[0]
    df[qID] = pd.to_numeric(df[qID], errors='coerce')
    df = df.dropna(subset=[qID])
    
    # Define question groups for comprehension.
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
    
    analysis_results = {
        "analysis_one": analysis_one(),
        "analysis_two": analysis_two(),
        "analysis_three": analysis_three(),
        "analysis_four": analysis_four()
    }
    
    if printText:
        print("Reading analysis (lang=%s) complete." % lang)
    
    return analysis_results

def plot_numeracy_results(analysis_results):
    """
    Create Plotly figures for numeracy analysis results.
    Returns a dictionary of figures.
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
        showlegend=False
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
        yaxis=dict(range=[0, 120], tickformat=".2f")
    )
    fig_gender.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    
    # Age-wise analysis
    age_analysis = analysis_results.get('analysis_age', {})
    age_data = {
        'Age': [],
        'Percentage': [],
        'Task': []
    }
    # Mapping from task label to analysis_age keys
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
            yaxis_title="Percentage of Students"
        )
    
    # Grade-wise analysis
    grade_analysis = analysis_results.get('analysis_grade', {})
    grade_data = {
        'Task': [],
        'Percentage': [],
        'Grade': []
    }
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
            yaxis=dict(range=[0, 120], tickformat=".2f")
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
    Create a Plotly bar chart for reading analysis results.
    
    Parameters:
    - results: Dictionary from reading_analysis.
    - lang: Language (e.g., "English" or "Nepali").
    - school_name: Name of the school (or "All") for labeling.
    
    Returns:
    A Plotly figure.
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
    fig.update_layout(yaxis=dict(range=[0, 100]))
    return fig

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
import os
import pandas as pd
import plotly.express as px

def load_data(filepath):
    """
    Load the CSV file into a pandas DataFrame.
    """
    df = pd.read_csv(filepath)
    return df

def numeracy_analysis(df, ids, school=None, printText=True):
    """
    Perform numeracy analysis on the provided DataFrame.
    
    Parameters:
    - df: DataFrame containing survey records.
    - ids: List of question IDs for the numeracy tasks.
    - school: Optional; if provided (and not "all"), filters the data to that school.
    - printText: If True, prints out additional info.
    
    Returns:
    A dictionary of analysis results.
    """
    # If a specific school is chosen, filter the DataFrame.
    if school is not None and school.lower() != "all":
        df = df[df['school'] == school]
    
    # If the DataFrame has multi-index columns, convert to single-level.
    if isinstance(df.columns, pd.MultiIndex):
        _ = {col[0]: col[1] for col in df.columns}
        df.columns = df.columns.get_level_values(0)
    
    total_students = df.shape[0]
    schools = df['school'].unique()
    genders = df['studentGender'].unique()
    
    # Define groups of question IDs (using the indices as in the original code)
    number_reading_qIDs = [ids[i] for i in [0, 1, 2, 3, 4, 5]]
    number_discrim_qIDs = [ids[i] for i in [6, 7, 8, 9, 10]]
    addition_qIDs = [ids[i] for i in [11, 12, 13, 14, 15]]
    pattern_recog_qIDs = [ids[i] for i in [18, 19, 20, 21]]
    
    # Define conditions for correct responses
    condition_reading = (df[number_reading_qIDs] == 'Correct').all(axis=1)
    condition_discrimination = (df[number_discrim_qIDs] == 'Correct').all(axis=1)
    condition_addition = (df[addition_qIDs] == 'Correct').all(axis=1)
    condition_pattern = (df[pattern_recog_qIDs] == 'Correct').all(axis=1)
    condition_all = condition_reading & condition_discrimination & condition_addition & condition_pattern

    # Helper to calculate overall and gender‐specific percentages
    def calculate_percentage_and_gender_results(condition):
        df_meeting = df[condition]
        count_meeting = df_meeting.shape[0]
        percentage_meeting = (count_meeting / total_students) * 100 if total_students else 0
        
        gender_results = {}
        for gender in genders:
            df_gender = df[df['studentGender'] == gender]
            total_gender = df_gender.shape[0]
            # Note: using the reading condition for gender breakdown (as in your original code)
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
    
    # Helper to calculate percentages by a grouping variable (age or grade)
    def calculate_percentage_by_age_or_grade(condition, group_by_col):
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
            "number_reading": calculate_percentage_by_age_or_grade(condition_reading, 'studentAge'),
            "number_discrimination": calculate_percentage_by_age_or_grade(condition_discrimination, 'studentAge'),
            "addition": calculate_percentage_by_age_or_grade(condition_addition, 'studentAge'),
            "pattern_recognition": calculate_percentage_by_age_or_grade(condition_pattern, 'studentAge'),
            "foundational_numeracy": calculate_percentage_by_age_or_grade(condition_all, 'studentAge')
        }

    def analysis_grade():
        return {
            "number_reading": calculate_percentage_by_age_or_grade(condition_reading, 'grade'),
            "number_discrimination": calculate_percentage_by_age_or_grade(condition_discrimination, 'grade'),
            "addition": calculate_percentage_by_age_or_grade(condition_addition, 'grade'),
            "pattern_recognition": calculate_percentage_by_age_or_grade(condition_pattern, 'grade'),
            "foundational_numeracy": calculate_percentage_by_age_or_grade(condition_all, 'grade')
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
        print("Number reading IDs:", number_reading_qIDs)
        print("Number discrimination IDs:", number_discrim_qIDs)
        print("Addition IDs:", addition_qIDs)
        print("Pattern recognition IDs:", pattern_recog_qIDs)
        print()
    
    return analysis_results

def reading_analysis(df, ids, total_words, lang="English", school=None, printText=True):
    """
    Perform reading analysis on the provided DataFrame.
    
    Parameters:
    - df: DataFrame with survey records.
    - ids: List of question IDs for the reading tasks.
    - total_words: Total word count of the story.
    - lang: Language of the test ("English" or "Nepali").
    - school: Optional; if provided (and not "all"), filters to that school.
    - printText: If True, prints additional info.
    
    Returns:
    A dictionary of analysis results.
    """
    if school is not None and school.lower() != "all":
        df = df[df['school'] == school]
    
    if isinstance(df.columns, pd.MultiIndex):
        _ = {col[0]: col[1] for col in df.columns}
        df.columns = df.columns.get_level_values(0)
    
    total_students = df.shape[0]
    schools = df['school'].unique()
    genders = df['studentGender'].unique()
    
    required_correct_words = int(0.9 * total_words)  # 90% threshold
    qID = ids[0]
    df[qID] = pd.to_numeric(df[qID], errors='coerce')
    df = df.dropna(subset=[qID])
    
    # Define question groups for comprehension.
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
    
    analysis_results = {
        "analysis_one": analysis_one(),
        "analysis_two": analysis_two(),
        "analysis_three": analysis_three(),
        "analysis_four": analysis_four()
    }
    
    if printText:
        print("Reading analysis (lang=%s) complete." % lang)
    
    return analysis_results

def plot_numeracy_results(analysis_results):
    """
    Create Plotly figures for numeracy analysis results.
    Returns a dictionary of figures.
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
        showlegend=False
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
        yaxis=dict(range=[0, 120], tickformat=".2f")
    )
    fig_gender.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    
    # Age-wise analysis
    age_analysis = analysis_results.get('analysis_age', {})
    age_data = {
        'Age': [],
        'Percentage': [],
        'Task': []
    }
    # Mapping from task label to analysis_age keys
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
            yaxis_title="Percentage of Students"
        )
    
    # Grade-wise analysis
    grade_analysis = analysis_results.get('analysis_grade', {})
    grade_data = {
        'Task': [],
        'Percentage': [],
        'Grade': []
    }
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
            yaxis=dict(range=[0, 120], tickformat=".2f")
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
    Create a Plotly bar chart for reading analysis results.
    
    Parameters:
    - results: Dictionary from reading_analysis.
    - lang: Language (e.g., "English" or "Nepali").
    - school_name: Name of the school (or "All") for labeling.
    
    Returns:
    A Plotly figure.
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
    fig.update_layout(yaxis=dict(range=[0, 100]))
    return fig

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
