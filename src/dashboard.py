# src/dashboard.py
import streamlit as st
import base64
import os

# Custom CSS for layout with green theme, 80rem max width
st.markdown(
    """
    <style>
    .main {
        max-width: 80rem; /* 1280px at 16px base font size */
        margin: 0 auto; /* Center the container */
        background-color: transparent; /* No coloring */
    }
    .dashboard-row {
        display: flex;
        align-items: center;
        max-height: 80px; /* Match logo height */
        overflow: hidden; /* Prevent overflow beyond 80px */
    }
    .logo-area {
        width: 20rem; /* 320px at 16px base font size */
        padding: 10px;
        text-align: center;
    }
    .header-area {
        flex-grow: 1;
        padding: 10px;
        background-color: #00695C; /* Green main color */
        border-radius: 8px; /* Rounded corners on all sides */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Subtle shadow for depth */
        max-height: 80px; /* Match row and logo height */
        line-height: 60px; /* Center text vertically within 80px */
        text-align: center;
        color: white; /* White text for contrast */
        font-family: 'Roboto', sans-serif; /* Professional font */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# First Row: Logo and Header
st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
col1, col2 = st.columns([20, 60])  # 20rem logo, remaining space for header (proportional to 80rem)
with col1:
    st.markdown('<div class="logo-area">', unsafe_allow_html=True)
    logo_path = "data/finagent_logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<img src="data:image/png;base64,{logo_base64}" '
            'style="display: block; max-height: 80px; margin: auto;" />',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span style='font-size: 40px; color: #4CAF50;'>📈</span>",
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown('<h1 class="header-area">FinAgent Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Placeholder for future rows
st.write("Second and third rows will be implemented in subsequent subtasks.")