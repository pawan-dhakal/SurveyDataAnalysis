# streamlit_app.py (Updated)
import streamlit as st
from foundational_survey import main as foundational_survey_main
from ict_in_education import main as ict_education_main

def inject_custom_css():
    st.markdown("""
    <style>
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
    }
    .hero-section {
        background: linear-gradient(135deg, #2C5F2D 0%, #97BC62FF 100%);
        padding: 4rem 2rem;
        border-radius: 15px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def home_page():
    st.markdown("""
    <div class="hero-section">
        <h1 style='color: white; text-align: center;'>
            Transforming Education in Rural Nepal
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Animated Metric Cards
    cols = st.columns(4)
    with cols[0]:
        st.markdown("""
        <div class="metric-card">
            <h3>📚 150+</h3>
            <p>Schools Supported</p>
            <small>+12% since 2022</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Add other cards...

    # Impact Stories
    with st.expander("🌟 Success Stories", expanded=True):
        st.video("https://youtu.be/olenepal_demo_video")
        st.caption("See how OLE Nepal transformed learning in Bajhang District")

def main():
    inject_custom_css()
    st.sidebar.image("https://olenepal.org/logo.png", use_container_width=True)
    
    page = st.sidebar.radio(
        "Navigate",
        ["🏠 Home", "📚 Learning Outcomes", "💻 ICT Resources"],
        horizontal=True
    )
    
    if page == "🏠 Home":
        home_page()
    elif page == "📚 Learning Outcomes":
        foundational_survey_main()
    elif page == "💻 ICT Resources":
        ict_education_main()

if __name__ == "__main__":
    main()