import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Market Analysis",
    page_icon="🏠",
    layout="wide"
)

# Inject custom CSS to hide ONLY the main app from the sidebar
hide_main_app_style = """ 
    <style> 
        [data-testid="stSidebarNav"] ul {
            padding-top: 2rem;
        }
        [data-testid="stSidebarNav"] ul li:first-child {
            display: none;
        }
    </style> 
""" 
st.markdown(hide_main_app_style, unsafe_allow_html=True)

# --- Data Loading and Preparation (as before) ---
# Your code for loading, combining, and cleaning data
business_df = pd.read_csv("business.csv")
facebook_df = pd.read_csv("Facebook.csv")
google_df = pd.read_csv("Google.csv")
tiktok_df = pd.read_csv("TikTok.csv")

facebook_df['source'] = 'Facebook'
google_df['source'] = 'Google'
tiktok_df['source'] = 'TikTok'

marketing_df = pd.concat([facebook_df, google_df, tiktok_df])

marketing_df['date'] = pd.to_datetime(marketing_df['date'])
business_df['date'] = pd.to_datetime(business_df['date'])

df = pd.merge(marketing_df, business_df, on="date", how="outer")
df = df.fillna(0)

