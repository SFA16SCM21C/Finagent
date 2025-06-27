# src/dashboard.py
import streamlit as st
import sqlite3
import pandas as pd
import os
from budgeting import apply_50_30_20_rule
from analysis import analyze_spending

# Store session state for savings plans and UI controls
if 'savings_plans' not in st.session_state:
    st.session_state.savings_plans = [{'goal': 0.0, 'saved': 0.0} for _ in range(4)]
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = None

# Custom CSS for green and grey theme
st.markdown(
    """
    <style>
    .main {
        max-width: 80rem;
    }
    .header-row {
        background-color: #4CAF50; /* Green primary color */
        padding: 10px;
        display: flex;
        align-items: center;
    }
    .logo-area {
        width: 33.33%;
        background-color: #808080; /* Grey secondary color */
        padding: 10px;
        text-align: center;
    }
    .title-area {
        width: 66.67%;
        color: white;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header Row
st.markdown('<div class="header-row">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])  # 1/3 logo, 2/3 header
with col1:
    st.markdown('<div class="logo-area">', unsafe_allow_html=True)
    st.image("data/finagent_logo.png", width=50)  # Placeholder logo
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="title-area">', unsafe_allow_html=True)
    st.title("FinAgent Dashboard")
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Placeholder for future rows
st.write("Second and third rows will be implemented in subsequent subtasks.")