import pandas as pd
import streamlit as st
import plotly.express as px

# Set page configuration
st.set_page_config(layout="wide", page_title="Marketing Dashboard")

# Load all the dataframes
business_df = pd.read_csv("Business.csv")
facebook_df = pd.read_csv("Facebook.csv")
google_df = pd.read_csv("Google.csv")
tiktok_df = pd.read_csv("TikTok.csv")

# Combine marketing data
marketing_df = pd.concat([facebook_df, google_df, tiktok_df])

# Convert date columns to datetime objects
marketing_df['date'] = pd.to_datetime(marketing_df['date'])
business_df['date'] = pd.to_datetime(business_df['date'])

# Merge the dataframes on the 'date' column
df = pd.merge(marketing_df, business_df, on="date", how="outer")

# Fill any NaN values that resulted from the merge with 0
df = df.fillna(0)

# Derive new key performance indicators (KPIs)
df['ROAS'] = df['attributed revenue'] / df['spend']
df['CPC'] = df['spend'] / df['clicks']
df['CTR'] = df['clicks'] / df['impression']
df['Click_to_Order_Conversion_Rate'] = df['# of orders'] / df['clicks']

# Dashboard title
st.title("Marketing Intelligence Dashboard")

# # Create sidebar filters
# st.sidebar.header("Filters")

# # Date range filter
# min_date = df['date'].min().date()
# max_date = df['date'].max().date()
# date_range = st.sidebar.date_input(
#     "Select Date Range",
#     [min_date, max_date],
#     min_value=min_date,
#     max_value=max_date
# )

# # Channel filter
# channels = df['tactic'].unique().tolist()
# selected_channels = st.sidebar.multiselect(
#     "Select Marketing Channels",
#     channels,
#     default=channels
# )

# # State filter
# states = df['state'].unique().tolist()
# selected_states = st.sidebar.multiselect(
#     "Select States",
#     states,
#     default=states
# )

# Filter the dataframe based on selections
filtered_df = df.copy()
if len(selected_channels) > 0:
    filtered_df = filtered_df[filtered_df['tactic'].isin(selected_channels)]
if len(selected_states) > 0:
    filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date) & 
                             (filtered_df['date'].dt.date <= end_date)]

# Store dataframes in session state for other pages to access
st.session_state['df'] = df
st.session_state['filtered_df'] = filtered_df

# Main page content
st.write("This is the main dashboard page. Navigate to the other pages using the sidebar.")

# Display some summary metrics
st.header("Summary Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Revenue", f"${filtered_df['total revenue'].sum():,.2f}")

with col2:
    st.metric("Total Orders", f"{filtered_df['# of orders'].sum():,.0f}")

with col3:
    st.metric("Marketing Spend", f"${filtered_df['spend'].sum():,.2f}")

with col4:
    st.metric("Overall ROAS", f"{filtered_df['attributed revenue'].sum() / filtered_df['spend'].sum():,.2f}")

# Print statements to see the transformed data
print("\n--- First 5 rows of the final dataframe ---")
print(df.head())

print("\n--- Summary statistics of the KPIs ---")
print(df[['ROAS', 'CPC', 'Click_to_Order_Conversion_Rate']].describe())

print("\n--- Sample data grouped by marketing channel ---")
print(df.groupby('tactic')[['spend', 'attributed revenue', 'ROAS']].mean())