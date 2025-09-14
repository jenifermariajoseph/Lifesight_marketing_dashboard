import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
# Import required libraries at the top of your file if not already imported
import plotly.graph_objects as go

# Load the data (same as in app.py)
business_df = pd.read_csv('Business.csv')  # Fixed case sensitivity
facebook_df = pd.read_csv('Facebook.csv')
google_df = pd.read_csv('Google.csv')
tiktok_df = pd.read_csv('TikTok.csv')

# Add source column to each dataframe before concatenation
facebook_df['source'] = 'Facebook'
google_df['source'] = 'Google'
tiktok_df['source'] = 'TikTok'

# Combine marketing data
marketing_df = pd.concat([facebook_df, google_df, tiktok_df])

# Convert date columns to datetime
business_df['date'] = pd.to_datetime(business_df['date'])
marketing_df['date'] = pd.to_datetime(marketing_df['date'])

# Merge data on date
df = pd.merge(marketing_df, business_df, on='date', how='outer')

# Fill NaN values with 0
df = df.fillna(0)

# Calculate KPIs
df['ROAS'] = df['attributed revenue'] / df['spend']  # Fixed column name
df['CPC'] = df['spend'] / df['clicks']
df['Click_to_Order_Conversion_Rate'] = df['# of orders'] / df['clicks']
df['CTR'] = df['clicks'] / df['impression'] * 100  # Click-Through Rate in percentage

# Calculate old customers (total orders - new customers)
df['old_customers'] = df['# of orders'] - df['new customers']

# Set page title
st.title('Business Overview')

# Date filter in sidebar
st.sidebar.header('Filters')
min_date = df['date'].min().date()
max_date = df['date'].max().date()
start_date = st.sidebar.date_input('Start date', min_date)
end_date = st.sidebar.date_input('End date', max_date)

# Filter data based on date selection
filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

# Calculate KPI metrics for the selected period
total_revenue = filtered_df['total revenue'].sum()
total_orders = filtered_df['# of orders'].sum()
total_profit = filtered_df['gross profit'].sum()
total_marketing_spend = filtered_df['spend'].sum()

# Calculate period-over-period changes (simulated for demonstration)
# In a real scenario, you would compare with previous period data
prev_period_revenue = total_revenue * 0.85  # Simulated previous period data
prev_period_orders = total_orders * 0.9
prev_period_profit = total_profit * 0.8
prev_period_spend = total_marketing_spend * 1.1

revenue_change = ((total_revenue / prev_period_revenue) - 1) * 100
orders_change = ((total_orders / prev_period_orders) - 1) * 100
profit_change = ((total_profit / prev_period_profit) - 1) * 100
spend_change = ((total_marketing_spend / prev_period_spend) - 1) * 100

# Function to create sparkline with improved styling
def create_sparkline(data, color):
    # Extract RGB values from the color string
    rgb_values = color.replace('rgb(', '').replace(')', '')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data,
        line=dict(color=color, width=2),
        mode='lines',
        fill='tozeroy',
        fillcolor=f'rgba({rgb_values}, 0.2)'
    ))
    fig.update_layout(
        height=60,  # Slightly taller for better visibility
        width=150,  # Wider to match the card width better
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True)
    )
    return fig

# After the function definition and before displaying KPI metrics

# Generate sample data for sparklines based on date range
dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Create trend data for sparklines
# For a real implementation, you would use actual historical data
revenue_trend = np.cumsum(np.random.normal(0, 1, size=len(dates))) + 100
profit_trend = np.cumsum(np.random.normal(0, 1, size=len(dates))) + 80
orders_trend = np.cumsum(np.random.normal(0, 0.5, size=len(dates))) + 50
spend_trend = np.cumsum(np.random.normal(0, 0.3, size=len(dates))) + 20

# Display KPI metrics in cards with sparklines
st.markdown("<h2 style='margin-bottom:0px;'>Key Performance Indicators</h2>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top:0px; margin-bottom:15px; border-color:rgba(255,255,255,0.2)'/>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Sales KPI with sparkline - improved styling
with col1:
    st.markdown(f"""
    <div style='background-color:#1e293b; padding:15px; border-radius:10px; height:150px;'>
        <div style='display:flex; justify-content:space-between;'>
            <h4 style='margin:0; color:#94a3b8; font-size:14px; font-weight:500;'>Sales</h4>
            <span style='color:#94a3b8; font-size:12px;'>CY {datetime.now().year}</span>
        </div>
        <h2 style='margin:5px 0; color:white; font-size:24px;'>${total_revenue:,.2f}</h2>
        <p style='margin:0; color:{'#4ade80' if revenue_change > 0 else '#ef4444'}; font-size:14px; font-weight:500;'>
            {'↑' if revenue_change > 0 else '↓'} {abs(revenue_change):.1f}%
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(create_sparkline(revenue_trend, 'rgb(56, 189, 248)'), width='stretch')

# Profit KPI with sparkline - improved styling
with col2:
    st.markdown(f"""
    <div style='background-color:#1e293b; padding:15px; border-radius:10px; height:150px;'>
        <div style='display:flex; justify-content:space-between;'>
            <h4 style='margin:0; color:#94a3b8; font-size:14px; font-weight:500;'>Profit</h4>
            <span style='color:#94a3b8; font-size:12px;'>CY {datetime.now().year}</span>
        </div>
        <h2 style='margin:5px 0; color:white; font-size:24px;'>${total_profit:,.2f}</h2>
        <p style='margin:0; color:{'#4ade80' if profit_change > 0 else '#ef4444'}; font-size:14px; font-weight:500;'>
            {'↑' if profit_change > 0 else '↓'} {abs(profit_change):.1f}%
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(create_sparkline(profit_trend, 'rgb(236, 72, 153)'), width='stretch')

# Orders KPI with sparkline - improved styling
with col3:
    st.markdown(f"""
    <div style='background-color:#1e293b; padding:15px; border-radius:10px; height:150px;'>
        <div style='display:flex; justify-content:space-between;'>
            <h4 style='margin:0; color:#94a3b8; font-size:14px; font-weight:500;'>Orders</h4>
            <span style='color:#94a3b8; font-size:12px;'>CY {datetime.now().year}</span>
        </div>
        <h2 style='margin:5px 0; color:white; font-size:24px;'>{int(total_orders):,}</h2>
        <p style='margin:0; color:{'#4ade80' if orders_change > 0 else '#ef4444'}; font-size:14px; font-weight:500;'>
            {'↑' if orders_change > 0 else '↓'} {abs(orders_change):.1f}%
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(create_sparkline(orders_trend, 'rgb(99, 102, 241)'), width='stretch')

# Marketing Spend KPI with sparkline - improved styling
with col4:
    # For marketing spend, lower is typically better
    spend_color = '#4ade80' if spend_change < 0 else '#ef4444'
    st.markdown(f"""
    <div style='background-color:#1e293b; padding:15px; border-radius:10px; height:150px;'>
        <div style='display:flex; justify-content:space-between;'>
            <h4 style='margin:0; color:#94a3b8; font-size:14px; font-weight:500;'>Marketing Spend</h4>
            <span style='color:#94a3b8; font-size:12px;'>CY {datetime.now().year}</span>
        </div>
        <h2 style='margin:5px 0; color:white; font-size:24px;'>${total_marketing_spend:,.2f}</h2>
        <p style='margin:0; color:{spend_color}; font-size:14px; font-weight:500;'>
            {'↓' if spend_change < 0 else '↑'} {abs(spend_change):.1f}%
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(create_sparkline(spend_trend, 'rgb(250, 204, 21)'), width='stretch')

# Continue with the rest of your code
# Company Comparison Section
st.header('Company Performance Comparison')

# Select metric for comparison
metric_options = {
    'Spend': 'spend',
    'Impressions': 'impression',
    'Clicks': 'clicks',
    'Attributed Revenue': 'attributed revenue',
    'ROAS': 'ROAS',
    'CPC': 'CPC',
    'CTR': 'CTR'
}

selected_metric = st.selectbox('Select Metric for Comparison', list(metric_options.keys()))
metric_column = metric_options[selected_metric]

# Group by source and calculate metrics
company_comparison = filtered_df.groupby('source').agg({
    'spend': 'sum',
    'impression': 'sum',
    'clicks': 'sum',
    'attributed revenue': 'sum'
}).reset_index()

# Calculate derived metrics
company_comparison['ROAS'] = company_comparison['attributed revenue'] / company_comparison['spend']
company_comparison['CPC'] = company_comparison['spend'] / company_comparison['clicks']
company_comparison['CTR'] = company_comparison['clicks'] / company_comparison['impression'] * 100

# Create bar chart for company comparison
fig_comparison = px.bar(
    company_comparison,
    x='source',
    y=metric_column,
    title=f'Company Comparison by {selected_metric}',
    color='source',
    text_auto='.2s'
)

# Customize the chart
fig_comparison.update_layout(
    xaxis_title='Company',
    yaxis_title=selected_metric,
    legend_title='Company'
)

st.plotly_chart(fig_comparison, use_container_width=True)

# Display the metrics table
st.subheader('Company Metrics Table')
formatted_comparison = company_comparison.copy()
formatted_comparison['spend'] = formatted_comparison['spend'].apply(lambda x: f"${x:,.2f}")
formatted_comparison['attributed revenue'] = formatted_comparison['attributed revenue'].apply(lambda x: f"${x:,.2f}")
formatted_comparison['ROAS'] = formatted_comparison['ROAS'].apply(lambda x: f"{x:.2f}")
formatted_comparison['CPC'] = formatted_comparison['CPC'].apply(lambda x: f"${x:.2f}")
formatted_comparison['CTR'] = formatted_comparison['CTR'].apply(lambda x: f"{x:.2f}%")
formatted_comparison.columns = ['Company', 'Spend', 'Impressions', 'Clicks', 'Attributed Revenue', 'ROAS', 'CPC', 'CTR']
st.dataframe(formatted_comparison, use_container_width=True)

# New vs Old Customers Line Chart
st.header('New vs Old Customers Over Time')

# Group by date and sum the customer metrics
customer_metrics = filtered_df.groupby('date').agg({
    'new customers': 'sum',
    'old_customers': 'sum'
}).reset_index()

# Melt dataframe into long format for easy plotting
customer_df = pd.melt(
    customer_metrics,
    id_vars=['date'],
    value_vars=['new customers', 'old_customers'],
    var_name='customer_type',
    value_name='count'
)

# Create the line chart
fig_customers = px.line(
    customer_df,
    x='date',
    y='count',
    color='customer_type',
    line_dash='customer_type',  # dashed vs solid lines
    title='New vs Old Customers Over Time',
    markers=True
)

# Customize the chart
fig_customers.update_layout(
    xaxis_title='Date',
    yaxis_title='Number of Customers',
    legend_title='Customer Type'
)

st.plotly_chart(fig_customers, use_container_width=True)

# Revenue vs. Profit Trend
st.header('Revenue vs. Profit Trend')

# Group by date and sum the metrics
daily_metrics = filtered_df.groupby('date').agg({
    'total revenue': 'sum',
    'gross profit': 'sum',
    'COGS': 'sum'
}).reset_index()

# Create the line chart
fig = px.line(daily_metrics, x='date', y=['total revenue', 'gross profit', 'COGS'],
              title='Daily Revenue vs. Profit',
              labels={'value': 'Amount ($)', 'variable': 'Metric'},
              color_discrete_sequence=['#0083B8', '#00B0A0', '#EF553B'])
st.plotly_chart(fig, use_container_width=True)

# Orders and New Customers Trend
st.header('Orders and New Customers Trend')

# Group by date and sum the metrics
orders_metrics = filtered_df.groupby('date').agg({
    '# of orders': 'sum',
    'new customers': 'sum'
}).reset_index()

# Create the line chart
fig2 = px.line(orders_metrics, x='date', y=['# of orders', 'new customers'],
               title='Daily Orders and New Customers',
               labels={'value': 'Count', 'variable': 'Metric'},
               color_discrete_sequence=['#0083B8', '#00B0A0'])
st.plotly_chart(fig2, use_container_width=True)

# Add this after the existing charts in your Overview page

# Animated Line Chart
st.header('Animated Revenue Trend')

# Group by date and get revenue metrics
daily_revenue = filtered_df.groupby('date')[['total revenue', 'attributed revenue', 'gross profit']].sum().reset_index()

# Create base figure
fig_animated = px.line(daily_revenue, x='date', y=['total revenue', 'attributed revenue', 'gross profit'],
                      title='Revenue Metrics Over Time (Animated)',
                      labels={'value': 'Amount ($)', 'variable': 'Metric'},
                      color_discrete_sequence=['#0083B8', '#00B0A0', '#EF553B'])

# Add animation
fig_animated.update_traces(mode='lines+markers')

# Create frames for animation
frames = []
for i in range(len(daily_revenue)):
    frame_data = daily_revenue.iloc[:i+1]
    frame = go.Frame(
        data=[
            go.Scatter(
                x=frame_data['date'],
                y=frame_data['total revenue'],
                mode='lines+markers',
                name='Total Revenue',
                line=dict(color='#0083B8', width=3),
                marker=dict(size=8)
            ),
            go.Scatter(
                x=frame_data['date'],
                y=frame_data['attributed revenue'],
                mode='lines+markers',
                name='Attributed Revenue',
                line=dict(color='#00B0A0', width=3),
                marker=dict(size=8)
            ),
            go.Scatter(
                x=frame_data['date'],
                y=frame_data['gross profit'],
                mode='lines+markers',
                name='Gross Profit',
                line=dict(color='#EF553B', width=3),
                marker=dict(size=8)
            )
        ],
        name=str(daily_revenue['date'].iloc[i].date())
    )
    frames.append(frame)

fig_animated.frames = frames

# Add animation controls with auto-play once
fig_animated.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            buttons=[
                dict(label="Replay",
                     method="animate",
                     args=[None, {"frame": {"duration": 100, "redraw": True},
                                  "fromcurrent": False,
                                  "transition": {"duration": 50, "easing": "cubic-in-out"}}])
            ],
            direction="left",
            pad={"r": 10, "t": 10},
            showactive=False,
            x=0.1,
            y=0,
            xanchor="right",
            yanchor="top"
        )
    ],
    # Smoother animation
    sliders=[dict(
        active=0,
        yanchor="top",
        xanchor="left",
        currentvalue=dict(
            font=dict(size=12),
            prefix="Date: ",
            visible=True,
            xanchor="right"
        ),
        pad=dict(b=10, t=50),
        len=0.9,
        x=0.1,
        y=0,
        transition=dict(duration=300, easing="cubic-in-out"),
        steps=[]
    )]
)

# Auto-play the animation once when displayed
fig_animated.update_layout(
    title="Revenue Metrics Over Time (Animated)",
    width=800,
    height=500
)

# Set animation to auto-play on load
st.plotly_chart(fig_animated, width='stretch', use_container_width=False)

# Add JavaScript to auto-play the animation once
st.markdown(
    """
    <script>
        setTimeout(function() {
            const buttons = document.querySelectorAll('button.modebar-btn[data-title="Play"]');
            if (buttons.length > 0) {
                buttons[buttons.length-1].click();
            }
        }, 1000);
    </script>
    """,
    unsafe_allow_html=True
)
