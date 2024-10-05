import pandas as pd
import streamlit as st
import plotly.express as px
import os

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
        )
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

# Path to the CSV file
csv_file_path = 'student_survey_data.csv'  # Update this to your actual CSV file path

# Load the data
df, question_dict = load_data(csv_file_path)

# Visualize the selected school data (all schools by default)
filtered_df = df  # Load data for both schools

# Sidebar for navigation
st.sidebar.title("Select Options")
# Removed file uploader, since we're loading directly from the file path

# Sidebar for selecting visualization
visualization_options = st.sidebar.radio("Select Question Set", 
    ("Read at home vs Read to at home", "Language at Home vs Language at School", "Other Question Set 1", "Other Question Set 2"))

# Define questions based on the selected option
if visualization_options == "Read at home vs Read to at home":
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
        filtered_grade_df = df[df['school'] == selected_schools_grade]
    else:
        filtered_grade_df = filtered_df  # Use filtered_df for both schools

    # Dropdown to select between Question 1 and Question 2 for grade distribution
    selected_question_grade = st.selectbox("Select Question for Grade Distribution",
        options=[question_dict[question_1], question_dict[question_2]], key='grade_question_dropdown')
    
    # Find the original question identifier based on the selected text
    question_key_grade = question_1 if selected_question_grade == question_dict[question_1] else question_2

    fig_grade = display_distribution_by_grade(filtered_grade_df, question_key_grade, selected_question_grade)
    st.plotly_chart(fig_grade)

# Add other visualizations for different question sets as needed...

