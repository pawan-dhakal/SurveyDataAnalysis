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

# -------------------------
# ANALYSIS PARAMETERS
# -------------------------
# drop FL27_cleaned5 for Siddhartha Kula Basic School and Ghami Solar Basic Schools because incorrect entries in the survey app
numeracy_ids = ["FL23_cleaned1", "FL23_cleaned2", "FL23_cleaned3", "FL23_cleaned4", "FL23_cleaned5", \
                 "FL23_cleaned6", "FL24_cleaned1", "FL24_cleaned2", "FL24_cleaned3", "FL24_cleaned4", "FL24_cleaned5", \
                 "FL25_cleaned1", "FL25_cleaned2", "FL25_cleaned3", "FL25_cleaned4", "FL25_cleaned5", \
                 "FL26", "FL26C", "FL27_cleaned1", "FL27_cleaned2", "FL27_cleaned3", "FL27_cleaned4",'FL27_cleaned5'] 

# READING TASKS ENGLISH
total_short_eng_words = 14
total_long_eng_words = 61
eng_reading_ids = ['FL13_cleaned','FL15','FL17',
                         'FL19_cleaned','FL21B_cleaned1','FL21B_cleaned2','FL21B_cleaned3','FL21B_cleaned4','FL21B_cleaned5']

long_eng_reading_ids = [eng_reading_ids[i] for i in [3,4,5,6,7,8]]
short_eng_reading_ids = [eng_reading_ids[i] for i in [0,1,2]]

# READING TASKS NEPALI
total_short_nep_words = 16
total_long_nep_words = 48
total_long_nep_words_1 = 60
nep_reading_ids = data = ["FL21G_cleaned", "FL21I", "FL21K", 
                          "FL21O_cleaned", "FL22_cleaned1", "FL22_cleaned2", "FL22_cleaned3", "FL22_cleaned4", "FL22_cleaned5"]
long_nep_reading_ids = [nep_reading_ids[i] for i in [3,4,5,6,7,8]]
short_nep_reading_ids = [nep_reading_ids[i] for i in [0,1,2]]

#for all schoools, the same English story (with names changed, no change in word count or question type)
#for Siddhartha Kula Basic School and Ghami Solar Basic School, use story1 ids for Nepali 

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
    pattern_recog_qIDs = [ids[i] for i in [18, 19, 20, 21]] #not included "FL27_cleaned5"

    # If school is not "Ghami Solar Basic School" or "Siddhartha Kula Basic School", include "FL27_cleaned5"
    if school not in ["Ghami Solar Basic School", "Siddhartha Kula Basic School"]:
        pattern_recog_qIDs.append("FL27_cleaned5")
            
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
def reading_analysis(df, ids, total_words_read=None, lang="English", school=None, printText=True):
    """
    Perform reading analysis on the provided DataFrame.
    Returns breakdowns by overall performance, gender, age, and grade.
    
    Parameters:
      - df: DataFrame containing survey records.
      - ids: List of question IDs for the reading task.
      - total_words_read: Optional override for the total number of words.
      - lang: "English" or "Nepali"
      - school: Filter by school (if provided)
      - printText: Whether to print a completion message.
    """
    # Filter by school if provided
    if school is not None and school.lower() != "all":
        df = df[df['school'] == school]
    
    # Determine if using the new Nepali story (for all schools except Ghami Solar Basic School and Siddhartha Kula Basic School)
    newNepaliStory = True
    if school in ["Ghami Solar Basic School", "Siddhartha Kula Basic School"]:
        newNepaliStory = False

    # Set total_words: override if total_words_read provided; otherwise, use defaults.
    if total_words_read is not None:
        total_words = total_words_read
    else:
        if lang == "English":
            total_words = 61
        elif lang == "Nepali" and newNepaliStory:
            total_words = 60
        elif lang == "Nepali" and not newNepaliStory:
            total_words = 48

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    total_students = df.shape[0]
    genders = df['studentGender'].unique()
    
    required_correct_words = int(0.9 * total_words)  # 90% threshold

    # The first ID (index 0) is assumed to hold the number of words read correctly.
    qID = ids[0]
    df.loc[:, qID] = pd.to_numeric(df[qID], errors='coerce')
    df = df.dropna(subset=[qID])
    
    # Define comprehension question groups based on language and story version.
    if lang == "English":
        # For English, use three literal questions and two inferential questions.
        lit_comp_qIDs = [ids[i] for i in [0, 1, 2, 3]]
        inf_comp_qIDs = [ids[i] for i in [0, 4, 5]]
        condition_lit_comp = (
            (df[qID] >= required_correct_words) &
            (df[lit_comp_qIDs[1]] == 'Correct') &
            (df[lit_comp_qIDs[2]] == 'Correct') &
            (df[lit_comp_qIDs[3]] == 'Correct')
        )
        condition_inf_comp = (
            (df[qID] >= required_correct_words) &
            (df[inf_comp_qIDs[1]].astype(str) == 'Correct') &
            (df[inf_comp_qIDs[2]].astype(str) == 'Correct')
        )
    elif lang == "Nepali" and not newNepaliStory:
        # For Nepali old story, mimic the English structure.
        lit_comp_qIDs = [ids[i] for i in [0, 1, 2, 3]]
        inf_comp_qIDs = [ids[i] for i in [0, 4, 5]]
        condition_lit_comp = (
            (df[qID] >= required_correct_words) &
            (df[lit_comp_qIDs[1]] == 'Correct') &
            (df[lit_comp_qIDs[2]] == 'Correct') &
            (df[lit_comp_qIDs[3]] == 'Correct')
        )
        condition_inf_comp = (
            (df[qID] >= required_correct_words) &
            (df[inf_comp_qIDs[1]].astype(str) == 'Correct') &
            (df[inf_comp_qIDs[2]].astype(str) == 'Correct')
        )
    elif lang == "Nepali" and newNepaliStory:
        # For Nepali new story, use one additional literal comprehension question and only one inferential question.
        lit_comp_qIDs = [ids[i] for i in [0, 1, 2, 3, 4]]
        inf_comp_qIDs = [ids[i] for i in [0, 5]]
        condition_lit_comp = (
            (df[qID] >= required_correct_words) &
            (df[lit_comp_qIDs[1]] == 'Correct') &
            (df[lit_comp_qIDs[2]] == 'Correct') &
            (df[lit_comp_qIDs[3]] == 'Correct') &
            (df[lit_comp_qIDs[4]] == 'Correct')
        )
        condition_inf_comp = (
            (df[qID] >= required_correct_words) &
            (df[inf_comp_qIDs[1]].astype(str) == 'Correct')
        )
    
    # Overall reading condition: words read plus both comprehension parts.
    condition_reading_story = df[qID] >= required_correct_words
    condition_all = condition_reading_story & condition_lit_comp & condition_inf_comp
    
    # Helper: Calculate percentages by a grouping column.
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
                                     (sub_df[inf_comp_qIDs[2]].astype(str) == 'Correct') if len(inf_comp_qIDs) > 2 
                                     else (sub_df[inf_comp_qIDs[1]].astype(str) == 'Correct')).sum() / total_gender * 100),
                    "foundational": (((sub_df[qID] >= required_correct_words) & 
                                      (sub_df[lit_comp_qIDs[1]] == 'Correct') & 
                                      (sub_df[lit_comp_qIDs[2]] == 'Correct') & 
                                      (sub_df[lit_comp_qIDs[3]] == 'Correct') &
                                      ((sub_df[inf_comp_qIDs[1]].astype(str) == 'Correct') & 
                                       (sub_df[inf_comp_qIDs[2]].astype(str) == 'Correct') if len(inf_comp_qIDs) > 2 
                                       else (sub_df[inf_comp_qIDs[1]].astype(str) == 'Correct'))).sum() / total_gender * 100)
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

def update_common_layout(fig, title, y_range=(0, 120), width=600):
    """
    Update the layout for a Plotly figure with consistent styling,
    reduced width, and internal legend placement.
    """
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        yaxis=dict(range=y_range, tickformat=".2f"),
        template='plotly_white',
        margin=dict(l=20, r=20, t=60, b=20),
        width=width,
        font=dict(size=12),
        legend=dict(
            x=0.75,
            y=0.95,
            bgcolor='rgba(255,255,255,0.6)',
            bordercolor='black',
            borderwidth=1
        )
    )
    return fig

def update_bar_traces(fig):
    """
    Update bar trace settings for better readability: show both percentage and count.
    """
    fig.update_traces(
        texttemplate='%{text:.2f}%<br>Count: %{customdata[0]}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Percentage: %{y:.2f}%<br>Count: %{customdata[0]}<extra></extra>'
    )
    return fig

def plot_numeracy_results(analysis_results):
    """
    Create Plotly figures for numeracy analysis results with improved styling,
    enhanced tooltips, internal legends, and text annotations that display both
    percentage and count values.
    """
    # Define task labels corresponding to each analysis result.
    task_labels = [
        'Number Reading',
        'Number Discrimination',
        'Addition',
        'Pattern Recognition',
        'Foundational Numeracy'
    ]
    
    # -------------------------
    # Overall Analysis Plot
    # -------------------------
    overall_data = [
        analysis_results['analysis_one']['percentage_meeting'],
        analysis_results['analysis_two']['percentage_meeting'],
        analysis_results['analysis_three']['percentage_meeting'],
        analysis_results['analysis_four']['percentage_meeting'],
        analysis_results['analysis_five']['percentage_meeting']
    ]
    overall_counts = [
        analysis_results['analysis_one']['count_meeting'],
        analysis_results['analysis_two']['count_meeting'],
        analysis_results['analysis_three']['count_meeting'],
        analysis_results['analysis_four']['count_meeting'],
        analysis_results['analysis_five']['count_meeting']
    ]
    
    overall_df = pd.DataFrame({
        'Task': task_labels,
        'Percentage': overall_data,
        'Count': overall_counts
    })
    
    fig_overall = px.bar(
        overall_df, 
        x='Task', 
        y='Percentage', 
        text='Percentage',
        custom_data=['Count'],
        color='Task',
        color_discrete_sequence=px.colors.qualitative.Set2,
        hover_data={"Count": True, "Percentage":":.2f"}
    )
    fig_overall = update_common_layout(fig_overall, "Overall Numeracy Task Completion Percentage", y_range=(0, 120))
    fig_overall = update_bar_traces(fig_overall)
    
    # -------------------------
    # Gender Analysis Plot
    # -------------------------
    male_percentages = []
    female_percentages = []
    male_counts = []
    female_counts = []
    for key in ['analysis_one', 'analysis_two', 'analysis_three', 'analysis_four', 'analysis_five']:
        male_data = analysis_results[key]['gender_results'].get('Male', {})
        female_data = analysis_results[key]['gender_results'].get('Female', {})
        male_percentages.append(male_data.get('percentage', 0))
        female_percentages.append(female_data.get('percentage', 0))
        male_counts.append(male_data.get('count', 0))
        female_counts.append(female_data.get('count', 0))
    
    gender_df = pd.DataFrame({
        'Task': task_labels * 2,
        'Percentage': male_percentages + female_percentages,
        'Count': male_counts + female_counts,
        'Gender': ['Male'] * 5 + ['Female'] * 5
    })
    
    fig_gender = px.bar(
        gender_df, 
        x='Task', 
        y='Percentage', 
        color='Gender',
        barmode='group', 
        text='Percentage',
        custom_data=['Count'],
        color_discrete_sequence=px.colors.qualitative.Set1,
        hover_data={"Count": True, "Percentage":":.2f"},
        title="Numeracy Task Completion by Gender"
    )
    fig_gender = update_common_layout(fig_gender, "Numeracy Task Completion by Gender", y_range=(0, 120))
    fig_gender = update_bar_traces(fig_gender)
    
    # -------------------------
    # Age Analysis Plot
    # -------------------------
    age_analysis = analysis_results.get('analysis_age', {})
    age_data = {'Age': [], 'Percentage': [], 'Task': [], 'Count': []}
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
                age_data['Percentage'].append(data.get('percentage', 0))
                age_data['Task'].append(task)
                # Use the correct field name for count.
                age_data['Count'].append(data.get('count_meeting', 0))
    age_fig = None
    if age_data['Age']:
        age_df = pd.DataFrame(age_data)
        # Pass the count as custom data.
        age_fig = px.line(
            age_df, 
            x='Age', 
            y='Percentage', 
            color='Task',
            markers=True,
            custom_data=['Count'],
            title="Numeracy Task Completion by Age",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        # For line plots, add text labels at each marker.
        age_fig.update_traces(
            text=age_df.apply(lambda row: f"{row['Percentage']:.2f}%\nCount: {row['Count']}", axis=1),
            textposition='top center',
            hovertemplate='<b>%{fullData.name}</b><br>Age: %{x}<br>Percentage: %{y:.2f}%<br>Count: %{customdata[0]}<extra></extra>'
        )
        age_fig = update_common_layout(age_fig, "Numeracy Task Completion by Age", y_range=(0, 140))
        age_fig.update_xaxes(title="Age (years)")
        age_fig.update_yaxes(title="Percentage of Students")
    
    # -------------------------
    # Grade Analysis Plot
    # -------------------------
    grade_analysis = analysis_results.get('analysis_grade', {})
    grade_data = {'Task': [], 'Percentage': [], 'Grade': [], 'Count': []}
    for task in task_labels:
        task_key = mapping.get(task)
        if task_key in grade_analysis:
            for grade_group, data in grade_analysis[task_key].items():
                grade_data['Task'].append(task)
                grade_data['Percentage'].append(data.get('percentage', 0))
                grade_data['Grade'].append(grade_group)
                # Correct count field
                grade_data['Count'].append(data.get('count_meeting', 0))
    grade_fig = None
    if grade_data['Task']:
        grade_df = pd.DataFrame(grade_data)
        grade_fig = px.bar(
            grade_df, 
            x='Task', 
            y='Percentage', 
            color='Grade',
            barmode='group', 
            text='Percentage',
            custom_data=['Count'],
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hover_data={"Count": True, "Percentage":":.2f"},
            title="Numeracy Task Completion by Grade"
        )
        grade_fig = update_common_layout(grade_fig, "Numeracy Task Completion by Grade", y_range=(0, 120))
        grade_fig = update_bar_traces(grade_fig)
    
    return {
        "fig_overall": fig_overall,
        "fig_gender": fig_gender,
        "fig_age": age_fig,
        "fig_grade": grade_fig
    }


def plot_reading_results(analysis_results, df, width=600):
    """
    Create Plotly figures for reading analysis results with improved styling,
    enhanced tooltips, internal legends, and text annotations that display both
    percentage and count values.
    
    Parameters:
      - analysis_results: Dictionary returned by reading_analysis.
      - df: The DataFrame used for analysis (used to compute group totals for gender and grade breakdowns).
      - width: Fixed width for the plots (default 600).
      
    Returns a dictionary with the following keys:
      - "fig_overall": Overall reading performance (words read, literal, inferential, foundational).
      - "fig_gender": Breakdown by gender.
      - "fig_age": Breakdown by age.
      - "fig_grade": Breakdown by grade.
    """
    # Define task labels
    tasks = [
        "Reading (Words)",
        "Literal Comprehension",
        "Inferential Comprehension",
        "Foundational Reading"
    ]
    
    # -------------------------
    # Overall Reading Performance
    # -------------------------
    overall_percentages = [
        analysis_results['analysis_one']['percentage_meeting'],
        analysis_results['analysis_two']['percentage_meeting'],
        analysis_results['analysis_three']['percentage_meeting'],
        analysis_results['analysis_four']['percentage_meeting']
    ]
    overall_counts = [
        analysis_results['analysis_one']['count_meeting'],
        analysis_results['analysis_two']['count_meeting'],
        analysis_results['analysis_three']['count_meeting'],
        analysis_results['analysis_four']['count_meeting']
    ]
    overall_df = pd.DataFrame({
        "Task": tasks,
        "Percentage": overall_percentages,
        "Count": overall_counts
    })
    fig_overall = px.bar(
        overall_df,
        x="Task",
        y="Percentage",
        text="Percentage",
        custom_data=["Count"],
        color="Task",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hover_data={"Count": True, "Percentage":":.1f"},
        title="Overall Reading Task Completion"
    )
    fig_overall.update_traces(
        texttemplate='%{text:.1f}%<br>Count: %{customdata[0]}',
        textposition='outside'
    )
    fig_overall = update_common_layout(fig_overall, "Overall Reading Task Completion", y_range=(0, 120), width=width)
    fig_overall = update_bar_traces(fig_overall)
    
    # -------------------------
    # Gender Breakdown
    # -------------------------
    # Compute totals for each gender from the dataframe
    gender_totals = df['studentGender'].value_counts().to_dict()
    gender_rows = []
    for gender, metrics in analysis_results["analysis_gender"].items():
        total_gender = gender_totals.get(gender, 0)
        for key, label in zip(
            ["read_words", "literal", "inferential", "foundational"],
            ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]
        ):
            count = round(metrics[key] * total_gender / 100)
            gender_rows.append({
                "Gender": gender,
                "Task": label,
                "Percentage": metrics[key],
                "Count": count
            })
    gender_df = pd.DataFrame(gender_rows)
    fig_gender = px.bar(
        gender_df,
        x="Task",
        y="Percentage",
        color="Gender",
        barmode="group",
        title="Reading Task Completion by Gender",
        text="Percentage",
        custom_data=["Count"],
        hover_data={"Count": True, "Percentage":":.1f"},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig_gender.update_traces(
        texttemplate='%{text:.1f}%<br>Count: %{customdata[0]}',
        textposition='outside'
    )
    fig_gender = update_common_layout(fig_gender, "Reading Task Completion by Gender", y_range=(0, 120), width=width)
    fig_gender = update_bar_traces(fig_gender)
    
    # -------------------------
    # Age Breakdown
    # -------------------------
    age_rows = []
    if "analysis_age" in analysis_results:
        for task_key, label in zip(
            ["read_words", "literal", "inferential", "foundational"],
            ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]
        ):
            if task_key in analysis_results["analysis_age"]:
                for age_group, data in analysis_results["analysis_age"][task_key].items():
                    age_rows.append({
                        "Age": age_group,
                        "Task": label,
                        "Percentage": data["percentage"],
                        "Count": data["count"]
                    })
    fig_age = None
    if age_rows:
        age_df = pd.DataFrame(age_rows)
        fig_age = px.line(
            age_df,
            x="Age",
            y="Percentage",
            color="Task",
            markers=True,
            custom_data=["Count"],
            title="Reading Task Completion by Age",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hover_data={"Count": True, "Percentage":":.1f"}
        )
        fig_age.update_traces(
            text=age_df.apply(lambda row: f"{row['Percentage']:.1f}%\nCount: {row['Count']}", axis=1),
            textposition='top center',
            hovertemplate='<b>%{fullData.name}</b><br>Age: %{x}<br>Percentage: %{y:.1f}%<br>Count: %{customdata[0]}<extra></extra>'
        )
        fig_age = update_common_layout(fig_age, "Reading Task Completion by Age", y_range=(0, 140), width=width)
        fig_age.update_xaxes(title="Age (years)")
        fig_age.update_yaxes(title="Percentage of Students")
    
    # -------------------------
    # Grade Breakdown
    # -------------------------
    grade_totals = df['grade'].value_counts().to_dict()
    grade_rows = []
    if "analysis_grade" in analysis_results:
        for task_key, label in zip(
            ["read_words", "literal", "inferential", "foundational"],
            ["Reading (Words)", "Literal Comprehension", "Inferential Comprehension", "Foundational Reading"]
        ):
            if task_key in analysis_results["analysis_grade"]:
                for grade_group, data in analysis_results["analysis_grade"][task_key].items():
                    total_grade = grade_totals.get(grade_group, 0)
                    count = round(data["percentage"] * total_grade / 100)
                    grade_rows.append({
                        "Grade": grade_group,
                        "Task": label,
                        "Percentage": data["percentage"],
                        "Count": count
                    })
    fig_grade = None
    if grade_rows:
        grade_df = pd.DataFrame(grade_rows)
        fig_grade = px.bar(
            grade_df,
            x="Task",
            y="Percentage",
            color="Grade",
            barmode="group",
            text="Percentage",
            custom_data=["Count"],
            title="Reading Task Completion by Grade",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hover_data={"Count": True, "Percentage":":.1f"}
        )
        fig_grade.update_traces(
            texttemplate='%{text:.1f}%<br>Count: %{customdata[0]}',
            textposition='outside'
        )
        fig_grade = update_common_layout(fig_grade, "Reading Task Completion by Grade", y_range=(0, 120), width=width)
        fig_grade = update_bar_traces(fig_grade)
    
    return {
        "fig_overall": fig_overall,
        "fig_gender": fig_gender,
        "fig_age": fig_age,
        "fig_grade": fig_grade
    }

def plot_overview_summary(df, numeracy_ids, eng_reading_ids, nep_reading_ids, width=800):
    """Generates key visual summaries for the surveyed schools based on the filtered data.

    Args:
        df (DataFrame): The filtered dataset of student survey responses.
        numeracy_ids (list): Question IDs for numeracy assessment.
        eng_reading_ids (list): Question IDs for English reading assessment.
        nep_reading_ids (list): Question IDs for Nepali reading assessment.
        width (int): Fixed width for the charts.

    Returns:
        dict: A dictionary containing summary metrics and Plotly figures.
    """
    # Summary Statistics
    total_students = len(df)
    total_schools = df['school'].nunique()

    # Aggregated school performance data (for each school, compute numeracy and reading performance)
    school_list = sorted(df['school'].unique().tolist())
    school_summary = []
    for school in school_list:
        school_df = df[df['school'] == school]
        numeracy_res = numeracy_analysis(school_df, numeracy_ids)
        eng_res = reading_analysis(school_df, eng_reading_ids, lang="English")
        nep_res = reading_analysis(school_df, nep_reading_ids, lang="Nepali")
        school_summary.append({
            "School": school,
            "Numeracy (%)": numeracy_res['analysis_five']['percentage_meeting'],
            "English Reading (%)": eng_res['analysis_four']['percentage_meeting'],
            "Nepali Reading (%)": nep_res['analysis_four']['percentage_meeting']
        })
    summary_df = pd.DataFrame(school_summary)

    # School performance comparison bar chart (grouped by school)
    fig_summary = px.bar(
        summary_df,
        x="School",
        y=["Numeracy (%)", "English Reading (%)", "Nepali Reading (%)"],
        barmode="group",
        title="Competency Comparison Across Schools",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_summary.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        width=width,
        margin=dict(l=40, r=40, t=60, b=60)
    )

    # Overall average performance across selected schools
    avg_numeracy = summary_df["Numeracy (%)"].mean()
    avg_eng = summary_df["English Reading (%)"].mean()
    avg_nep = summary_df["Nepali Reading (%)"].mean()
    avg_df = pd.DataFrame({
        "Category": ["Numeracy", "English Reading", "Nepali Reading"],
        "Average (%)": [avg_numeracy, avg_eng, avg_nep]
    })
    fig_performance = px.bar(
        avg_df,
        x="Category",
        y="Average (%)",
        title="Average Performance Across Selected Schools",
        text="Average (%)",
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_performance.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    fig_performance.update_layout(
        autosize=True,
        width=width,
        margin=dict(l=40, r=40, t=60, b=60)
    )

    # Gender distribution pie chart
    gender_counts = df['studentGender'].value_counts()
    fig_gender = px.pie(
        values=gender_counts.values,
        names=gender_counts.index,
        title="Gender Distribution",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig_gender.update_layout(
        autosize=True,
        width=width,
        margin=dict(l=40, r=40, t=60, b=60)
    )

    # Grade distribution bar chart
    grade_counts = df['grade'].value_counts().sort_index()
    fig_grade = px.bar(
        x=grade_counts.index,
        y=grade_counts.values,
        labels={'x': 'Grade', 'y': 'Number of Students'},
        title="Grade Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_grade.update_layout(
        autosize=True,
        width=width,
        margin=dict(l=40, r=40, t=60, b=60)
    )

    # Age distribution histogram: using 'studentAge'
    fig_age = px.histogram(
        df,
        x="studentAge",
        title="Age Distribution of Students",
        nbins=15,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_age.update_layout(
        autosize=True,
        width=width,
        margin=dict(l=40, r=40, t=60, b=60)
    )

    return {
        "total_students": total_students,
        "total_schools": total_schools,
        "fig_summary": fig_summary,
        "fig_performance": fig_performance,
        "fig_gender": fig_gender,
        "fig_grade": fig_grade,
        "fig_age": fig_age
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
