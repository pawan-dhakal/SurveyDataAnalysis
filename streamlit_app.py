import pandas as pd
import streamlit as st
import plotly.express as px

# Function to load and prepare data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file, header=[0, 1])
    question_dict = {col[0]: col[1] for col in df.columns}
    df.columns = df.columns.get_level_values(0)  # Use only the first row for columns
    return df, question_dict

# Function to clean response data
def clean_responses(response_series):
    return response_series.str.strip().str.lower()

# Function to display heatmap
def display_heatmap(filtered_df, question_1, question_2, question_dict):
    # Clean response columns
    filtered_df[question_1] = clean_responses(filtered_df[question_1])
    filtered_df[question_2] = clean_responses(filtered_df[question_2])
    
    # Count responses
    comparison_data = filtered_df.groupby([question_1, question_2]).size().reset_index(name='Count')

    # Create a DataFrame for all combinations of Yes/No responses
    all_combinations = pd.MultiIndex.from_product([['yes', 'no'], ['yes', 'no']], names=[question_1, question_2])
    comparison_data = comparison_data.set_index([question_1, question_2]).reindex(all_combinations, fill_value=0).reset_index()

    # Create heatmap data
    heatmap_data = comparison_data.pivot(index=question_2, columns=question_1, values='Count').fillna(0)

    # Plot the heatmap
    fig_heatmap = px.imshow(
        heatmap_data,
        labels={'x': question_dict[question_1], 'y': question_dict[question_2], 'color': 'Count'},
        text_auto=True,  # Enable text inside cells
        color_continuous_scale='Blues'
    )
    
    # Update layout for better appearance
    fig_heatmap.update_layout(
        title="Number of Students Responses",
        xaxis_title=question_dict[question_1],
        yaxis_title=question_dict[question_2],
        coloraxis_colorbar=dict(
            title="Number of Students",
            ticks="outside"
        )
    )
    
    return fig_heatmap  # Return the figure instead of displaying it here

# Function to display distribution by age
def display_distribution_by_age(filtered_df, question, question_text):
    # Clean response column
    filtered_df[question] = clean_responses(filtered_df[question])
    
    age_distribution = filtered_df.groupby(['studentAge', question]).size().reset_index(name='Count')
    fig_age = px.bar(age_distribution, x='studentAge', y='Count', color=question, 
                     title=f'Response Distribution by Age: {question_text}',
                     labels={'Count': 'Number of Students', 'studentAge': 'Age'},
                     barmode='group')
    return fig_age  # Return the figure instead of displaying it here

# Function to display distribution by grade
def display_distribution_by_grade(filtered_df, question, question_text):
    # Clean response column
    filtered_df[question] = clean_responses(filtered_df[question])
    
    grade_distribution = filtered_df.groupby(['grade', question]).size().reset_index(name='Count')
    fig_grade = px.bar(grade_distribution, x='grade', y='Count', color=question, 
                       title=f'Response Distribution by Grade: {question_text}',
                       labels={'Count': 'Number of Students', 'grade': 'Grade'},
                       barmode='group')
    return fig_grade  # Return the figure instead of displaying it here


# Custom function to convert survey time to minutes
def convert_to_minutes(time_str):
    """Converts survey time from 'HH:MM:SS' to total minutes."""
    minutes, seconds, milliseconds = map(int, time_str.split(':'))
    total_minutes = minutes + seconds / 60 + milliseconds/3600
    return total_minutes

# Function to display summary plots
def display_summary_plots(df):
    # Summary: Total Students
    total_students = df.shape[0]
    
    # Calculate total male and female students
    gender_counts = df['studentGender'].value_counts()
    total_male = gender_counts.get('Male', 0)
    total_female = gender_counts.get('Female', 0)

    # Calculate percentages
    male_percentage = (total_male / total_students) * 100 if total_students > 0 else 0
    female_percentage = (total_female / total_students) * 100 if total_students > 0 else 0

    # Display total students and gender percentages on the same line
    st.subheader("Total Students and Gender Distribution")
    st.write(f"Total Students: {total_students} | Male: {total_male} ({male_percentage:.2f}%) | Female: {total_female} ({female_percentage:.2f}%)")
    
    # Distribution of Ages
    st.subheader("Distribution of Ages")
    age_distribution = df.groupby(['studentAge', 'school']).size().reset_index(name='Count')
    fig_age_dist = px.bar(age_distribution, x='studentAge', y='Count', color='school',
                           title='Age Distribution of Students',
                           labels={'Count': 'Number of Students', 'studentAge': 'Age'},
                           barmode='group')
    st.plotly_chart(fig_age_dist)

    # Distribution of Grades
    st.subheader("Distribution of Grades")
    grade_distribution = df.groupby(['grade', 'school']).size().reset_index(name='Count')
    fig_grade_dist = px.bar(grade_distribution, x='grade', y='Count', color='school',
                             title='Grade Distribution of Students',
                             labels={'Count': 'Number of Students', 'grade': 'Grade'},
                             barmode='group')
    st.plotly_chart(fig_grade_dist)

    # Distribution by School
    st.subheader("Distribution by School")
    school_distribution = df['school'].value_counts().reset_index()
    school_distribution.columns = ['School', 'Count']
    fig_school_dist = px.pie(school_distribution, names='School', values='Count',
                              title='Distribution of Students by School')
    st.plotly_chart(fig_school_dist)

    # Gender Distribution by Grade
    st.subheader("Gender Distribution by Grade")
    gender_by_grade = df.groupby(['grade', 'studentGender']).size().reset_index(name='Count')
    fig_gender_grade = px.bar(gender_by_grade, x='grade', y='Count', color='studentGender',
                               title='Gender Distribution by Grade',
                               labels={'Count': 'Number of Students', 'grade': 'Grade'},
                               barmode='group')
    st.plotly_chart(fig_gender_grade)

    # Survey Time Distribution
    st.subheader("Survey Completion Time Distribution")
    # Convert 'elapsedTime' using the custom function
    df['ElapsedMinutes'] = df['elapsedTime'].apply(convert_to_minutes)

    # Create histogram for survey times grouped by school
    fig_time_dist = px.histogram(df, x='ElapsedMinutes', color='school', 
                                  title='Distribution of Survey Completion Times (in minutes)',
                                  labels={'ElapsedMinutes': 'Time Taken (minutes)'},
                                  nbins=50)
    st.plotly_chart(fig_time_dist)

    # Box plot for survey times
    st.subheader("Box Plot of Survey Completion Times")
    fig_box_plot = px.box(df, x='school', y='ElapsedMinutes',
                           title='Box Plot of Survey Completion Times by School',
                           labels={'ElapsedMinutes': 'Time Taken (minutes)', 'school': 'School'})
    st.plotly_chart(fig_box_plot)

    # Optionally, display the average survey time
    avg_time = df['ElapsedMinutes'].mean()
    avg_minutes = int(avg_time)
    avg_seconds = int((avg_time - avg_minutes) * 60)
    st.write(f"Average Survey Time: {avg_minutes} minutes {avg_seconds} seconds")

# Function to display heatmap for FL7 and FL9A
def display_language_heatmap(filtered_df, question_1, question_2, question_dict):
    # Clean response columns
    filtered_df[question_1] = clean_responses(filtered_df[question_1])
    filtered_df[question_2] = clean_responses(filtered_df[question_2])
    
    # Count responses
    comparison_data = filtered_df.groupby([question_1, question_2]).size().reset_index(name='Count')

    # Get unique language options from the DataFrame
    language_options_1 = filtered_df[question_1].unique()
    language_options_2 = filtered_df[question_2].unique()
    
    # Create a DataFrame for all combinations of unique language responses
    all_combinations = pd.MultiIndex.from_product([language_options_1, language_options_2], names=[question_1, question_2])
    comparison_data = comparison_data.set_index([question_1, question_2]).reindex(all_combinations, fill_value=0).reset_index()

    # Create heatmap data
    heatmap_data = comparison_data.pivot(index=question_2, columns=question_1, values='Count').fillna(0)

    # Plot the heatmap
    fig_heatmap = px.imshow(
        heatmap_data,
        labels={'x': question_dict[question_1], 'y': question_dict[question_2], 'color': 'Count'},
        text_auto=True,  # Enable text inside cells
        color_continuous_scale='Blues'
    )
    
    # Update layout for better appearance
    fig_heatmap.update_layout(
        title="Language Responses Comparison",
        xaxis_title=question_dict[question_1],
        yaxis_title=question_dict[question_2],
        coloraxis_colorbar=dict(
            title="Number of Students",
            ticks="outside"
        ),
        xaxis=dict(tickfont=dict(size=10)),  # Adjust font size for x-axis labels
        yaxis=dict(tickfont=dict(size=10)),  # Adjust font size for y-axis labels
    )
    
    return fig_heatmap

# Function to display distribution of languages
def display_language_distribution(filtered_df, question, question_text):
    # Clean response column
    filtered_df[question] = clean_responses(filtered_df[question])
    
    language_distribution = filtered_df.groupby(question).size().reset_index(name='Count')
    fig_lang = px.bar(language_distribution, x=question, y='Count', 
                      title=f'Distribution of Languages: {question_text}',
                      labels={'Count': 'Number of Students', question: 'Language'},
                      color=question)
    return fig_lang
# Sidebar for navigation
st.sidebar.title("Select Options")
uploaded_file = st.sidebar.file_uploader("Upload your student survey CSV file", type="csv")
#uploaded_file = 'student_survey_records.csv'
# Load the data if a file is uploaded
if uploaded_file is not None:
    df, question_dict = load_data(uploaded_file)

    # Visualize the selected school data (all schools by default)
    filtered_df = df  # Load data for both schools

    # Sidebar for selecting visualization
    visualization_options = st.sidebar.radio("Select Question Set", 
        ("Summary", "Read at home vs Read to at home", "Language at Home vs Language at School", "Other Question Set 1", "Other Question Set 2"))

    if visualization_options == "Summary":
        st.header("Survey Summary")
        display_summary_plots(filtered_df)

    elif visualization_options == "Read at home vs Read to at home":
        question_1 = 'FL6_cleaned1'
        question_2 = 'FL6_cleaned2'
        
        # Page title for the current visualization
        st.header("Read at Home vs Read to at Home")

        # Display heatmap for the selected questions
        st.subheader("Heatmap of Responses - Number of Students")
        
        # Dropdown for filtering by school for the heatmap
        selected_schools_heatmap = st.selectbox("Select Schools for Heatmap", 
            options=["Both Schools"] + list(df['school'].unique()), key='heatmap_dropdown')
        
        # Filter data based on selected schools for heatmap
        if selected_schools_heatmap != "Both Schools":
            filtered_df = filtered_df[filtered_df['school'] == selected_schools_heatmap]

        fig_heatmap = display_heatmap(filtered_df, question_1, question_2, question_dict)
        st.plotly_chart(fig_heatmap)

        # Distribution by age
        st.subheader("Distribution of Responses by Age")
        
        # Dropdown for filtering by school for age distribution
        selected_schools_age = st.selectbox("Select Schools for Age Distribution", 
            options=["Both Schools"] + list(df['school'].unique()), key='age_dropdown')
        
        # Filter data based on selected schools for age distribution
        if selected_schools_age != "Both Schools":
            filtered_age_df = df[df['school'] == selected_schools_age]
        else:
            filtered_age_df = filtered_df  # Use filtered_df for both schools

        # Dropdown to select between Question 1 and Question 2 for age distribution
        selected_question_age = st.selectbox("Select Question for Age Distribution",
            options=[question_dict[question_1], question_dict[question_2]], key='age_question_dropdown')
        
        # Find the original question identifier based on the selected text
        question_key_age = question_1 if selected_question_age == question_dict[question_1] else question_2

        fig_age = display_distribution_by_age(filtered_age_df, question_key_age, selected_question_age)
        st.plotly_chart(fig_age)

        # Distribution by grade
        st.subheader("Distribution of Responses by Grade")
        
        # Dropdown for filtering by school for grade distribution
        selected_schools_grade = st.selectbox("Select Schools for Grade Distribution", 
            options=["Both Schools"] + list(df['school'].unique()), key='grade_dropdown')
        
        # Filter data based on selected schools for grade distribution
        if selected_schools_grade != "Both Schools":
            filtered_grade_df = filtered_df[filtered_df['school'] == selected_schools_grade]
        else:
            filtered_grade_df = filtered_df  # Use filtered_df for both schools

        # Dropdown to select between Question 1 and Question 2 for grade distribution
        selected_question_grade = st.selectbox("Select Question for Grade Distribution",
            options=[question_dict[question_1], question_dict[question_2]], key='grade_question_dropdown')
        
        # Find the original question identifier based on the selected text
        question_key_grade = question_1 if selected_question_grade == question_dict[question_1] else question_2

        fig_grade = display_distribution_by_grade(filtered_grade_df, question_key_grade, selected_question_grade)
        st.plotly_chart(fig_grade)

    elif visualization_options == "Language at Home vs Language at School":
        question_1 = 'FL7'
        question_2 = 'FL9A'
        question_1_text = question_dict[question_1]
        question_2_text = question_dict[question_2]
        
        # Page title for the current visualization
        st.header("Language at Home vs Language at School")

        # Display heatmap for the selected language questions
        st.subheader("Heatmap of Language Responses - Number of Students")
        
        # Dropdown for filtering by school for the heatmap
        selected_schools_heatmap_lang = st.selectbox("Select Schools for Language Heatmap", 
            options=["Both Schools"] + list(df['school'].unique()), key='language_heatmap_dropdown')
        
        # Filter data based on selected schools for heatmap
        if selected_schools_heatmap_lang != "Both Schools":
            filtered_df_lang = filtered_df[filtered_df['school'] == selected_schools_heatmap_lang]
        else:
            filtered_df_lang = filtered_df  # Use filtered_df for both schools

        fig_heatmap_lang = display_language_heatmap(filtered_df_lang, question_1, question_2, question_dict)
        st.plotly_chart(fig_heatmap_lang)

        # Distribution of languages spoken at home
        st.subheader("Distribution of Languages Spoken at Home")
        
        fig_lang_home = display_language_distribution(filtered_df_lang, question_1, question_dict[question_1])
        st.plotly_chart(fig_lang_home)

        # Distribution of languages spoken at school
        st.subheader("Distribution of Languages Spoken at School")
        
        fig_lang_school = display_language_distribution(filtered_df_lang, question_2, question_dict[question_2])
        st.plotly_chart(fig_lang_school)