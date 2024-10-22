import streamlit as st

from foundational_survey import main as foundational_survey_main
#from offline_servers import main as offline_servers_main
#from ict_in_education import main as ict_education_main

# Main title for the dashboard
st.title("Dashboard Navigation")

# Create a selection option to navigate between dashboards
option = st.selectbox(
    "Select a dashboard to view:",
    ("Home", "Foundational Survey Dashboard", "ICT in Education Dashboard","Offline Servers Dashboard")
)

# Conditional rendering of each dashboard based on the selected option
if option == "Foundational Survey Dashboard":
    foundational_survey_main()  # Runs the foundational_survey.py dashboard

elif option == "Offline Servers Dashboard":
    #offline_servers_main()  # Runs the offline_servers.py dashboard
    st.write("OFFLINE SERVERS VISUALIZATION HERE")

elif option == "ICT in Education Dashboard":
    ict_education_main()  # Runs the offline_servers.py dashboard
    

else:
    st.write("Welcome to the main dashboard! Select a dashboard to view from the options above.")
