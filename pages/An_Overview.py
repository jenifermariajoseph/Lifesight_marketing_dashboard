import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# --- Data Loading and Preparation (as before) ---
# Your code for loading, combining, and cleaning data
business_df = pd.read_csv("business.csv")
facebook_df = pd.read_csv("Facebook.csv")
google_df = pd.read_csv("Google.csv")
tiktok_df = pd.read_csv("TikTok.csv")

facebook_df['source'] = 'Facebook'
google_df['source'] = 'Google'
tiktok_df['source'] = 'TikTok'
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

marketing_df = pd.concat([facebook_df, google_df, tiktok_df])

marketing_df['date'] = pd.to_datetime(marketing_df['date'])
business_df['date'] = pd.to_datetime(business_df['date'])

df = pd.merge(marketing_df, business_df, on="date", how="outer")
df = df.fillna(0)

# Derive new key performance indicators (KPIs)
df['ROAS'] = df['attributed revenue'] / df['spend']
df['CPC'] = df['spend'] / df['clicks']
df['CTR'] = df['clicks'] / df['impression']
df['Click_to_Order_Conversion_Rate'] = df['# of orders'] / df['clicks']

# --- Dashboard UI and Theming ---

st.set_page_config(layout="wide", page_title="Optimal Marketing Dashboard")

st.markdown("""
    <style>
    .kpi-card {
        background-color: #1E2130;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        height: 100%;
    }
    .main-header {
        color: #FFFFFF;
        font-size: 36px;
        text-align: left;
        margin-bottom: 20px;
        padding-left: 20px;
        padding-top: 10px;
    }
    .subheader {
        color: #A3A8B8;
        font-size: 14px;
        margin-top: 0;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 28px;
        font-weight: bold;
        margin-top: 10px;
    }
    .metric-change-pos {
        color: #4CAF50;
        font-size: 16px;
    }
    .metric-change-neg {
        color: #F44336;
        font-size: 16px;
    }
    .plot-container {
        padding: 0;
        background-color: #1E2130;
        border-radius: 10px;
        height: 100%;
        margin-top: 20px;
    }
    .reportview-container .main {
        background-color: #0A0C1A;
    }
    </style>
""", unsafe_allow_html=True)


# --- Sidebar Filters ---
st.sidebar.header("Filters")
min_date = df['date'].min().date()
max_date = df['date'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['date'].dt.date >= start_date) & 
                     (df['date'].dt.date <= end_date)]
else:
    st.warning("Please select a valid date range.")
    st.stop()


# --- KPI Metrics Calculation ---
# Current period data
total_revenue = filtered_df['total revenue'].sum()
total_orders = filtered_df['# of orders'].sum()
total_spend = filtered_df['spend'].sum()
# Fix ROAS calculation to use total_revenue instead of attributed revenue
overall_roas = total_revenue / total_spend if total_spend > 0 else 0

# Last month data calculation
current_month = start_date.month
current_year = start_date.year

# Handle previous month (accounting for year change)
if current_month == 1:  # January
    last_month = 12  # December
    last_month_year = current_year - 1
else:
    last_month = current_month - 1
    last_month_year = current_year

# Filter data for last month
last_month_df = df[(df['date'].dt.month == last_month) & 
                  (df['date'].dt.year == last_month_year)]

# Calculate last month metrics
last_month_revenue = last_month_df['total revenue'].sum()
last_month_orders = last_month_df['# of orders'].sum()
last_month_spend = last_month_df['spend'].sum()
# Fix ROAS calculation for last month
last_month_roas = last_month_revenue / last_month_spend if last_month_spend > 0 else 0

# Calculate percentage changes compared to last month
revenue_change = ((total_revenue - last_month_revenue) / last_month_revenue) * 100 if last_month_revenue != 0 else 0
orders_change = ((total_orders - last_month_orders) / last_month_orders) * 100 if last_month_orders != 0 else 0
spend_change = ((total_spend - last_month_spend) / last_month_spend) * 100 if last_month_spend != 0 else 0
roas_change = ((overall_roas - last_month_roas) / last_month_roas) * 100 if last_month_roas != 0 else 0


# Compare with data from 2 weeks ago
two_weeks_ago_start = start_date - timedelta(days=14)
two_weeks_ago_end = end_date - timedelta(days=14)

two_weeks_ago_df = df[(df['date'].dt.date >= two_weeks_ago_start) & 
                     (df['date'].dt.date <= two_weeks_ago_end)]

# Calculate metrics from 2 weeks ago
two_weeks_ago_revenue = two_weeks_ago_df['total revenue'].sum()
two_weeks_ago_orders = two_weeks_ago_df['# of orders'].sum()
two_weeks_ago_spend = two_weeks_ago_df['spend'].sum()
two_weeks_ago_roas = two_weeks_ago_revenue / two_weeks_ago_spend if two_weeks_ago_spend > 0 else 0

# Compare with data from a month ago
month_ago_start = start_date - timedelta(days=30)
month_ago_end = end_date - timedelta(days=30)

month_ago_df = df[(df['date'].dt.date >= month_ago_start) & 
                     (df['date'].dt.date <= month_ago_end)]

# Calculate metrics from a month ago
month_ago_revenue = month_ago_df['total revenue'].sum()
month_ago_orders = month_ago_df['# of orders'].sum()
month_ago_spend = month_ago_df['spend'].sum()
month_ago_roas = month_ago_revenue / month_ago_spend if month_ago_spend > 0 else 0

# Calculate percentage changes with a cap to prevent extreme values
def calculate_capped_change(current, previous, cap=100):
    if previous == 0 or previous < 0.01 * current:  # Prevent division by zero or very small values
        return cap if current > 0 else -cap
    change = ((current - previous) / previous) * 100
    return max(min(change, cap), -cap)  # Cap between -100% and +100%

# Calculate percentage changes with reasonable caps
revenue_change = calculate_capped_change(total_revenue, month_ago_revenue)
orders_change = calculate_capped_change(total_orders, month_ago_orders)
spend_change = calculate_capped_change(total_spend, month_ago_spend)
roas_change = calculate_capped_change(overall_roas, month_ago_roas)


# --- Sparkline Charts ---
time_series_data = filtered_df.groupby('date').agg({
    'total revenue': 'sum',
    '# of orders': 'sum',
    'spend': 'sum'
}).reset_index()
# Calculate ROAS directly from total_revenue and spend
time_series_data['ROAS'] = time_series_data['total revenue'] / time_series_data['spend']
time_series_data = time_series_data.fillna(0)

def create_sparkline(data, x_col, y_col, color):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines',
            line=dict(width=2, color=color),
            showlegend=False
        )
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=100,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showticklabels=True, showgrid=False, zeroline=False, title=dict(text=x_col, font=dict(size=10))),
        yaxis=dict(showticklabels=True, showgrid=False, zeroline=False, title=dict(text=y_col, font=dict(size=10)))
    )
    return fig

# Create sparkline charts
revenue_sparkline = create_sparkline(time_series_data, 'date', 'total revenue', '#66C2FF')
orders_sparkline = create_sparkline(time_series_data, 'date', '# of orders', '#66FFB2')
spend_sparkline = create_sparkline(time_series_data, 'date', 'spend', '#FFD166')
roas_sparkline = create_sparkline(time_series_data, 'date', 'ROAS', '#FF6699')

# --- Main Dashboard Layout ---
st.markdown("<h1 class='main-header'>Marketing Analysis Dashboard</h1>", unsafe_allow_html=True)

# KPI Cards Section
col1, col2, col3, col4 = st.columns(4)

# Update the KPI card styling in the markdown sections

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <h3 style="color:#A3A8B8; font-size:16px; margin:0; padding:0;">Total Revenue</h3>
            <p style="color:#FFFFFF; font-size:12px; margin:0; padding:0;">CURRENT PERIOD</p>
            <h1 style="color:#FFFFFF; font-size:28px; margin:5px 0 0 0; padding:0;">${total_revenue:,.2f}</h1>
            <p style="color:{'#4CAF50' if revenue_change > 0 else '#F44336'}; font-size:14px; margin:0; padding:0;">
                {'↑' if revenue_change > 0 else '↓'} {abs(revenue_change):.1f}% from 2 weeks prior
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(revenue_sparkline, use_container_width=True, config={'displayModeBar': False})

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <h3 style="color:#A3A8B8; font-size:16px; margin:0; padding:0;">Total Orders</h3>
            <p style="color:#FFFFFF; font-size:12px; margin:0; padding:0;">CURRENT PERIOD</p>
            <h1 style="color:#FFFFFF; font-size:28px; margin:5px 0 0 0; padding:0;">{total_orders:,}</h1>
            <p style="color:{'#4CAF50' if orders_change > 0 else '#F44336'}; font-size:14px; margin:0; padding:0;">
                {'↑' if orders_change > 0 else '↓'} {abs(orders_change):.1f}% from 2 weeks prior
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(orders_sparkline, use_container_width=True, config={'displayModeBar': False})

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <h3 style="color:#A3A8B8; font-size:16px; margin:0; padding:0;">Total Spend</h3>
            <p style="color:#FFFFFF; font-size:12px; margin:0; padding:0;">CURRENT PERIOD</p>
            <h1 style="color:#FFFFFF; font-size:28px; margin:5px 0 0 0; padding:0;">${total_spend:,.2f}</h1>
            <p style="color:{'#4CAF50' if spend_change > 0 else '#F44336'}; font-size:14px; margin:0; padding:0;">
                {'↑' if spend_change > 0 else '↓'} {abs(spend_change):.1f}% from 2 weeks prior
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(spend_sparkline, use_container_width=True, config={'displayModeBar': False})

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <h3 style="color:#A3A8B8; font-size:16px; margin:0; padding:0;">Overall ROAS</h3>
            <p style="color:#FFFFFF; font-size:12px; margin:0; padding:0;">CURRENT PERIOD</p>
            <h1 style="color:#FFFFFF; font-size:28px; margin:5px 0 0 0; padding:0;">{overall_roas:.2f}</h1>
            <p style="color:{'#4CAF50' if roas_change > 0 else '#F44336'}; font-size:14px; margin:0; padding:0;">
                {'↑' if roas_change > 0 else '↓'} {abs(roas_change):.1f}% from 2 weeks prior
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(roas_sparkline, use_container_width=True, config={'displayModeBar': False})

# Main charts section
st.markdown("<h2 style='color:white; margin-top: 40px; text-align: left;'>Marketing and Business Trends</h2>", unsafe_allow_html=True)
main_chart_col1, main_chart_col2 = st.columns(2)

with main_chart_col1:
    st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:white; padding: 10px;'>Revenue & Spend Over Time</h3>", unsafe_allow_html=True)
    
    # Get daily performance data with source breakdown
    daily_performance = filtered_df.groupby('date').agg({
        'total revenue': 'sum',
        'attributed revenue': 'sum',  # Add attributed revenue sum
        'spend': 'sum'
    }).reset_index()
    
    # Get revenue breakdown by source for each date
    source_revenue = filtered_df.groupby(['date', 'source']).agg({
        'attributed revenue': 'sum'
    }).reset_index()
    
    # Create a dictionary to store revenue breakdown by date
    revenue_breakdown = {}
    for date in daily_performance['date']:
        date_str = date.strftime('%Y-%m-%d')
        date_data = source_revenue[source_revenue['date'] == date]
        
        # Calculate total attributed revenue for this date
        total_attributed = daily_performance[daily_performance['date'] == date]['attributed revenue'].values[0]
        
        # Create hover text with revenue breakdown
        breakdown_text = f"<b>Total Attributed Revenue</b>: ${total_attributed:,.2f}<br><br>"
        
        for _, row in date_data.iterrows():
            if row['attributed revenue'] > 0:
                source = row['source']
                revenue = row['attributed revenue']
                percentage = (revenue / total_attributed * 100) if total_attributed > 0 else 0
                breakdown_text += f"<b>{source}</b>: ${revenue:,.2f} ({percentage:.1f}%)<br>"
        
        revenue_breakdown[date_str] = breakdown_text
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add revenue trace to primary y-axis with custom hover template
    fig.add_trace(go.Scatter(
        x=daily_performance['date'],
        y=daily_performance['total revenue'],
        name='total revenue',
        line=dict(color='#66FFB2', width=2),
        hovertemplate=(
            "<b>Date</b>: %{x|%Y-%m-%d}<br>" +
            "<b>Total Revenue</b>: $%{y:,.2f}<br><br>" +
            "<b>Revenue Breakdown:</b><br>" +
            "%{customdata}<br>"
        ),
        customdata=[revenue_breakdown.get(date.strftime('%Y-%m-%d'), "No breakdown available") 
                   for date in daily_performance['date']]
    ))
    
    # Add spend trace to secondary y-axis
    fig.add_trace(go.Scatter(
        x=daily_performance['date'],
        y=daily_performance['spend'],
        name='spend',
        line=dict(color='#FFD166', width=2),
        yaxis='y2'
    ))
    
    # Set layout with two y-axes
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        legend_title_text='',
        yaxis=dict(title='Revenue ($)', showgrid=True, gridcolor='#2E3244'),
        yaxis2=dict(title='Spend ($)', overlaying='y', side='right', showgrid=False),
        xaxis=dict(showgrid=False),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='rgba(50, 50, 50, 0.8)',
            font_size=12,
            font_family="Arial"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
with main_chart_col2:
    st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:white; padding: 10px;'>Orders and New Customers Over Time</h3>", unsafe_allow_html=True)
    daily_orders = filtered_df.groupby('date').agg({
        '# of orders': 'sum',
        'new customers': 'sum'
    }).reset_index()
    
    # Create figure with secondary y-axis
    fig_combined = go.Figure()
    
    # Add total orders trace to primary y-axis
    fig_combined.add_trace(go.Scatter(
        x=daily_orders['date'],
        y=daily_orders['# of orders'],
        name='Total Orders',
        line=dict(color='#66C2FF', width=2)
    ))
    
    # Add new customers trace to secondary y-axis
    fig_combined.add_trace(go.Scatter(
        x=daily_orders['date'],
        y=daily_orders['new customers'],
        name='New Customers',
        line=dict(color='#FF6699', width=2),
        yaxis='y2'
    ))
    
    # Set layout with two y-axes
    fig_combined.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        yaxis=dict(title='Total Orders', showgrid=True, gridcolor='#2E3244'),
        yaxis2=dict(title='New Customers', overlaying='y', side='right', showgrid=False),
        xaxis=dict(showgrid=False),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_combined, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Remove the separate New Customers Over Time chart since it's now combined
    # st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
    # st.markdown("<h3 style='color:white; padding: 10px;'>New Customers Over Time</h3>", unsafe_allow_html=True)
    # fig_new_customers = px.line(
    #     daily_orders,
    #     x='date',
    #     y='new customers',
    #     labels={'value': 'Count', 'date': 'Date'},
    #     color_discrete_sequence=['#FF6699']
    # )
    # fig_new_customers.update_layout(
    #     paper_bgcolor='rgba(0,0,0,0)',
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     font_color='white'
    # )
    # fig_new_customers.update_xaxes(showgrid=False)
    # fig_new_customers.update_yaxes(showgrid=True, gridcolor='#2E3244')
    # st.plotly_chart(fig_new_customers, use_container_width=True)
    # st.markdown("</div>", unsafe_allow_html=True)

# After the New Customers Over Time chart
st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; padding: 10px;'>Orders vs Revenue Analysis</h3>", unsafe_allow_html=True)

# Group by date and calculate daily metrics
daily_metrics = filtered_df.groupby('date').agg({
    'new customers': 'sum',
    '# of orders': 'sum',
    '# of new orders': 'sum',
    'attributed revenue': 'sum',
    'total revenue': 'sum'
}).reset_index()

# Calculate repeat orders
daily_metrics['repeat_orders'] = daily_metrics['# of orders'] - daily_metrics['# of new orders']

# Calculate revenue from new orders vs repeat orders (estimated based on order proportion)
daily_metrics['new_orders_revenue'] = (daily_metrics['# of new orders'] / daily_metrics['# of orders'] * 
                                     daily_metrics['total revenue']).fillna(0)
daily_metrics['repeat_orders_revenue'] = (daily_metrics['repeat_orders'] / daily_metrics['# of orders'] * 
                                        daily_metrics['total revenue']).fillna(0)

# Calculate correlations between orders and revenue
new_orders_revenue_corr = daily_metrics['# of new orders'].corr(daily_metrics['new_orders_revenue'])
repeat_orders_revenue_corr = daily_metrics['repeat_orders'].corr(daily_metrics['repeat_orders_revenue'])
total_orders_revenue_corr = daily_metrics['# of orders'].corr(daily_metrics['total revenue'])

# Function to get color based on correlation strength
def get_corr_color(corr_value):
    if corr_value >= 0.7:
        return "#82CD47"  # Strong positive - green
    elif corr_value >= 0.4:
        return "#FFD966"  # Moderate positive - yellow
    elif corr_value >= 0.1:
        return "#FFA500"  # Weak positive - orange
    elif corr_value >= -0.1:
        return "#CCCCCC"  # Negligible - gray
    elif corr_value >= -0.4:
        return "#FF6B6B"  # Weak negative - light red
    elif corr_value >= -0.7:
        return "#E74C3C"  # Moderate negative - red
    else:
        return "#B71C1C"  # Strong negative - dark red

# Create the line chart comparing new orders revenue vs repeat orders revenue
fig_orders_revenue = go.Figure()

# Add trace for new orders revenue
fig_orders_revenue.add_trace(go.Scatter(
    x=daily_metrics['date'],
    y=daily_metrics['new_orders_revenue'],
    mode='lines+markers',
    name='New Orders Revenue',
    line=dict(color='#82CD47', width=3),
    marker=dict(size=8)
))

# Add trace for repeat orders revenue
fig_orders_revenue.add_trace(go.Scatter(
    x=daily_metrics['date'],
    y=daily_metrics['repeat_orders_revenue'],
    mode='lines+markers',
    name='Repeat Orders Revenue',
    line=dict(color='#4B56D2', width=3),
    marker=dict(size=8)
))

# Calculate totals for annotations
total_new_orders_revenue = daily_metrics['new_orders_revenue'].sum()
total_repeat_orders_revenue = daily_metrics['repeat_orders_revenue'].sum()
total_revenue = total_new_orders_revenue + total_repeat_orders_revenue

# Calculate percentages
new_orders_revenue_pct = (total_new_orders_revenue / total_revenue) * 100 if total_revenue > 0 else 0
repeat_orders_revenue_pct = (total_repeat_orders_revenue / total_revenue) * 100 if total_revenue > 0 else 0

# Add analytics annotations - shifted upward
fig_orders_revenue.add_shape(
    type="rect",
    x0=daily_metrics['date'].min(),
    y0=daily_metrics['repeat_orders_revenue'].max() * 0.6,  # Shifted upward
    x1=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.3,
    y1=daily_metrics['repeat_orders_revenue'].max() * 1.2,  # Shifted upward
    fillcolor="rgba(30, 33, 48, 0.8)",
    line=dict(width=0),
    layer="below"
)

# Shifted annotations upward
fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 1.15,  # Shifted upward
    text=f"<b>Revenue Breakdown</b>",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 1.08,  # Shifted upward
    text=f"New Orders: <b style='color:#82CD47'>${total_new_orders_revenue:,.2f} ({new_orders_revenue_pct:.1f}%)</b>",
    showarrow=False,
    font=dict(color="white", size=10),
    align="left"
)

fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 1.01,  # Shifted upward
    text=f"Repeat Orders: <b style='color:#4B56D2'>${total_repeat_orders_revenue:,.2f} ({repeat_orders_revenue_pct:.1f}%)</b>",
    showarrow=False,
    font=dict(color="white", size=10),
    align="left"
)

# Add correlation annotations - shifted upward
fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 0.94,  # Shifted upward
    text=f"<b>Correlation Analysis</b>",
    showarrow=False,
    font=dict(color="white", size=10),
    align="left"
)

fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 0.87,  # Shifted upward
    text=f"New Orders to Revenue: <b style='color:{get_corr_color(new_orders_revenue_corr)}'>{new_orders_revenue_corr:.2f}</b>",
    showarrow=False,
    font=dict(color="white", size=9),
    align="left"
)

fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 0.80,  # Shifted upward
    text=f"Repeat Orders to Revenue: <b style='color:{get_corr_color(repeat_orders_revenue_corr)}'>{repeat_orders_revenue_corr:.2f}</b>",
    showarrow=False,
    font=dict(color="white", size=9),
    align="left"
)

# Update layout
fig_orders_revenue.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    xaxis_title='Date',
    yaxis_title='Revenue ($)',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    hovermode='x unified',
    margin=dict(l=60, r=60, t=30, b=60)
)

fig_orders_revenue.update_xaxes(showgrid=False)
fig_orders_revenue.update_yaxes(showgrid=True, gridcolor='#2E3244', tickprefix='$', tickformat=',')

st.plotly_chart(fig_orders_revenue, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# After the New Customers vs Orders relationship section
st.markdown("<h2 style='color:white; margin-top: 40px; text-align: left;'>Sales Tactics Performance</h2>", unsafe_allow_html=True)

# Create a new container for the tactics vs revenue visualization
st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; padding: 10px;'>Sales Growth Analysis For Top Tactics for the Last Month</h3>", unsafe_allow_html=True)

# Aggregate data by tactic and source to get revenue contribution
tactics_data = filtered_df.groupby(['tactic', 'source']).agg({
    'attributed revenue': 'sum'
}).reset_index()

# Create a combined label for tactic and source
tactics_data['tactic_source'] = tactics_data['tactic'] + ' - ' + tactics_data['source']

# Sort by revenue and get top 5 tactic-source combinations
top_tactics = tactics_data.sort_values('attributed revenue', ascending=False).head(5)

# Calculate previous period for comparison (a month ago)
month_ago_tactics = month_ago_df.groupby(['tactic', 'source']).agg({
    'attributed revenue': 'sum'
}).reset_index()

# Create the same combined label for previous period
month_ago_tactics['tactic_source'] = month_ago_tactics['tactic'] + ' - ' + month_ago_tactics['source']

# Merge current and previous period data
tactics_comparison = pd.merge(top_tactics, month_ago_tactics, 
                             on='tactic_source', how='left', 
                             suffixes=('_current', '_previous'))

# Calculate growth percentage
tactics_comparison['growth_pct'] = tactics_comparison.apply(
    lambda x: calculate_capped_change(x['attributed revenue_current'], 
                                     x['attributed revenue_previous']), 
    axis=1
)

# Define bolder, more vibrant colors for growth indicators
POSITIVE_COLOR = '#00E676'  # Bright green
NEGATIVE_COLOR = '#FF1744'  # Bright red

# Create the lollipop chart
fig = go.Figure()

# Add the bars
fig.add_trace(go.Bar(
    y=tactics_comparison['tactic_source'],
    x=tactics_comparison['attributed revenue_current'],
    orientation='h',
    marker=dict(
        color='rgba(31, 58, 147, 0.6)',
        line=dict(color='rgba(31, 58, 147, 1.0)', width=1)
    ),
    name='Revenue'
))

# Add the markers at the end of the bars
fig.add_trace(go.Scatter(
    y=tactics_comparison['tactic_source'],
    x=tactics_comparison['attributed revenue_current'],
    mode='markers',
    marker=dict(
        color='rgb(31, 119, 180)',
        size=14,  # Slightly larger markers
        line=dict(color='rgb(31, 119, 180)', width=1)
    ),
    name='Revenue Point'
))

# Add annotations for growth percentages with bolder colors and styling
for i, row in tactics_comparison.iterrows():
    growth_color = POSITIVE_COLOR if row['growth_pct'] > 0 else NEGATIVE_COLOR
    growth_symbol = '▲' if row['growth_pct'] > 0 else '▼'
    
    fig.add_annotation(
        y=row['tactic_source'],
        x=row['attributed revenue_current'],
        text=f"<b>${row['attributed revenue_current']:,.2f}</b> {growth_symbol} <b>{abs(row['growth_pct']):.1f}%</b>",
        showarrow=True,
        arrowhead=0,
        arrowcolor=growth_color,
        arrowwidth=3,  # Thicker arrow
        arrowsize=1.5,  # Larger arrow
        ax=50,  # Slightly more offset
        ay=0,
        font=dict(
            size=14,  # Larger font
            color=growth_color,
            family="Arial Black, sans-serif",  # Bolder font
        ),
        align="left"
    )

# Update layout
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    height=400,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(
        title='Revenue ($)',
        showgrid=True,
        gridcolor='#2E3244',
        zeroline=False
    ),
    yaxis=dict(
        title='',
        showgrid=False,
        zeroline=False
    ),
    showlegend=False,
    hovermode='closest'
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Calculate correlation coefficients
corr_new_orders_revenue = daily_metrics['# of new orders'].corr(daily_metrics['new_orders_revenue'])
corr_repeat_orders_revenue = daily_metrics['repeat_orders'].corr(daily_metrics['repeat_orders_revenue'])
corr_total_orders_revenue = daily_metrics['# of orders'].corr(daily_metrics['total revenue'])

# Determine color for correlation values
def corr_color(corr_value):
    if corr_value > 0.7:
        return "#4CAF50"  # strong positive (green)
    elif corr_value > 0.3:
        return "#8BC34A"  # moderate positive (light green)
    elif corr_value > 0:
        return "#FFC107"  # weak positive (yellow)
    elif corr_value > -0.3:
        return "#FF9800"  # weak negative (orange)
    elif corr_value > -0.7:
        return "#FF5722"  # moderate negative (light red)
    else:
        return "#F44336"  # strong negative (red)

# Add correlation analysis section to the annotations
fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 0.75,
    text=f"<b>Correlation Analysis</b>",
    showarrow=False,
    font=dict(color="white", size=14),
    align="left"
)

fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 0.65,
    text=f"New Orders → Revenue: <b style='color:{corr_color(corr_new_orders_revenue)}'>{corr_new_orders_revenue:.2f}</b>",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 0.55,
    text=f"Repeat Orders → Revenue: <b style='color:{corr_color(corr_repeat_orders_revenue)}'>{corr_repeat_orders_revenue:.2f}</b>",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

fig_orders_revenue.add_annotation(
    x=daily_metrics['date'].min() + (daily_metrics['date'].max() - daily_metrics['date'].min()) * 0.05,
    y=daily_metrics['repeat_orders_revenue'].max() * 0.45,
    text=f"Total Orders → Revenue: <b style='color:{corr_color(corr_total_orders_revenue)}'>{corr_total_orders_revenue:.2f}</b>",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)