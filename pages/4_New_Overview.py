import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# --- Data Loading and Preparation (as before) ---
# Your code for loading, combining, and cleaning data
business_df = pd.read_csv("Business.csv")
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

# Calculate percentage changes with a cap to prevent extreme values
def calculate_capped_change(current, previous, cap=100):
    if previous == 0 or previous < 0.01 * current:  # Prevent division by zero or very small values
        return cap if current > 0 else -cap
    change = ((current - previous) / previous) * 100
    return max(min(change, cap), -cap)  # Cap between -100% and +100%

# Calculate percentage changes with reasonable caps
revenue_change = calculate_capped_change(total_revenue, two_weeks_ago_revenue)
orders_change = calculate_capped_change(total_orders, two_weeks_ago_orders)
spend_change = calculate_capped_change(total_spend, two_weeks_ago_spend)
roas_change = calculate_capped_change(overall_roas, two_weeks_ago_roas)


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
st.markdown("<h1 class='main-header'>Optimal Dashboard for Marketing Analysis</h1>", unsafe_allow_html=True)

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
    daily_performance = filtered_df.groupby('date').agg({
        'total revenue': 'sum',
        'spend': 'sum'
    }).reset_index()
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add revenue trace to primary y-axis
    fig.add_trace(go.Scatter(
        x=daily_performance['date'],
        y=daily_performance['total revenue'],
        name='total revenue',
        line=dict(color='#66FFB2', width=2)
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
        xaxis=dict(showgrid=False)
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
st.markdown("<h3 style='color:white; padding: 10px;'>Relationship: New Customers vs Orders</h3>", unsafe_allow_html=True)

# Group by date and calculate daily metrics
daily_metrics = filtered_df.groupby('date').agg({
    'new customers': 'sum',
    '# of orders': 'sum',
    '# of new orders': 'sum'
}).reset_index()

# Calculate repeat orders
daily_metrics['repeat_orders'] = daily_metrics['# of orders'] - daily_metrics['# of new orders']

# Calculate percentage analytics
total_orders = filtered_df['# of orders'].sum()
new_orders = filtered_df['# of new orders'].sum()
repeat_orders = total_orders - new_orders
new_customers = filtered_df['new customers'].sum()

# Calculate percentages
new_orders_pct = (new_orders / total_orders) * 100 if total_orders > 0 else 0
repeat_orders_pct = (repeat_orders / total_orders) * 100 if total_orders > 0 else 0

# Calculate average orders per new customer
orders_per_customer = new_orders / new_customers if new_customers > 0 else 0

# Calculate correlation coefficient between new customers and new orders
corr_new_customers_new_orders = daily_metrics['new customers'].corr(daily_metrics['# of new orders'])
corr_new_customers_repeat_orders = daily_metrics['new customers'].corr(daily_metrics['repeat_orders'])
corr_new_customers_total_orders = daily_metrics['new customers'].corr(daily_metrics['# of orders'])

# Create a scatter plot showing the relationship
fig_customer_orders = go.Figure()

# Add scatter plot for new orders vs new customers
fig_customer_orders.add_trace(go.Scatter(
    x=daily_metrics['new customers'],
    y=daily_metrics['# of new orders'],
    mode='markers',
    name='New Orders',
    marker=dict(size=10, color='#82CD47', opacity=0.7),
    hovertemplate='New Customers: %{x}<br>New Orders: %{y}'
))

# Add scatter plot for repeat orders vs new customers
fig_customer_orders.add_trace(go.Scatter(
    x=daily_metrics['new customers'],
    y=daily_metrics['repeat_orders'],
    mode='markers',
    name='Repeat Orders',
    marker=dict(size=10, color='#4B56D2', opacity=0.7),
    hovertemplate='New Customers: %{x}<br>Repeat Orders: %{y}'
))

# Add scatter plot for total orders vs new customers
fig_customer_orders.add_trace(go.Scatter(
    x=daily_metrics['new customers'],
    y=daily_metrics['# of orders'],
    mode='markers',
    name='Total Orders',
    marker=dict(size=12, color='#FF6B6B', opacity=0.7),
    hovertemplate='New Customers: %{x}<br>Total Orders: %{y}'
))

# Add trend lines
for trace_name in ['New Orders', 'Repeat Orders', 'Total Orders']:
    if trace_name == 'New Orders':
        y_data = daily_metrics['# of new orders']
        color = '#82CD47'
    elif trace_name == 'Repeat Orders':
        y_data = daily_metrics['repeat_orders']
        color = '#4B56D2'
    else:  # Total Orders
        y_data = daily_metrics['# of orders']
        color = '#FF6B6B'
    
    # Add trend line
    z = np.polyfit(daily_metrics['new customers'], y_data, 1)
    p = np.poly1d(z)
    x_range = np.linspace(min(daily_metrics['new customers']), max(daily_metrics['new customers']), 100)
    
    fig_customer_orders.add_trace(go.Scatter(
        x=x_range,
        y=p(x_range),
        mode='lines',
        line=dict(color=color, dash='dash'),
        name=f'{trace_name} Trend',
        showlegend=False
    ))

# Add analytics annotations directly on the graph
# Create a semi-transparent background for analytics
fig_customer_orders.add_shape(
    type="rect",
    x0=min(daily_metrics['new customers']),
    y0=max(daily_metrics['# of orders']) * 0.6,
    x1=min(daily_metrics['new customers']) + (max(daily_metrics['new customers']) - min(daily_metrics['new customers'])) * 0.35,
    y1=max(daily_metrics['# of orders']),
    fillcolor="rgba(30, 33, 48, 0.8)",
    line=dict(width=0),
    layer="below"
)

# Add analytics text annotations
fig_customer_orders.add_annotation(
    x=min(daily_metrics['new customers']) + (max(daily_metrics['new customers']) - min(daily_metrics['new customers'])) * 0.05,
    y=max(daily_metrics['# of orders']) * 0.95,
    text=f"<b>Order Analytics</b>",
    showarrow=False,
    font=dict(color="white", size=14),
    align="left"
)

fig_customer_orders.add_annotation(
    x=min(daily_metrics['new customers']) + (max(daily_metrics['new customers']) - min(daily_metrics['new customers'])) * 0.05,
    y=max(daily_metrics['# of orders']) * 0.9,
    text=f"New Orders: <b style='color:#82CD47'>{new_orders_pct:.1f}%</b>",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

fig_customer_orders.add_annotation(
    x=min(daily_metrics['new customers']) + (max(daily_metrics['new customers']) - min(daily_metrics['new customers'])) * 0.05,
    y=max(daily_metrics['# of orders']) * 0.85,
    text=f"Repeat Orders: <b style='color:#4B56D2'>{repeat_orders_pct:.1f}%</b>",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

fig_customer_orders.add_annotation(
    x=min(daily_metrics['new customers']) + (max(daily_metrics['new customers']) - min(daily_metrics['new customers'])) * 0.05,
    y=max(daily_metrics['# of orders']) * 0.8,
    text=f"Orders per Customer: <b>{orders_per_customer:.2f}</b>",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

fig_customer_orders.add_annotation(
    x=min(daily_metrics['new customers']) + (max(daily_metrics['new customers']) - min(daily_metrics['new customers'])) * 0.05,
    y=max(daily_metrics['# of orders']) * 0.75,
    text=f"<b>Correlation Analysis</b>",
    showarrow=False,
    font=dict(color="white", size=14),
    align="left"
)

# Determine color for correlation values
def corr_color(corr_value):
    if corr_value > 0.5:
        return "#4CAF50"  # positive (green)
    elif corr_value > 0:
        return "#FFC107"  # neutral (yellow)
    else:
        return "#F44336"  # negative (red)

fig_customer_orders.add_annotation(
    x=min(daily_metrics['new customers']) + (max(daily_metrics['new customers']) - min(daily_metrics['new customers'])) * 0.05,
    y=max(daily_metrics['# of orders']) * 0.7,
    text=f"New Customers → New Orders: <b style='color:{corr_color(corr_new_customers_new_orders)}'>{corr_new_customers_new_orders:.2f}</b>",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

fig_customer_orders.add_annotation(
    x=min(daily_metrics['new customers']) + (max(daily_metrics['new customers']) - min(daily_metrics['new customers'])) * 0.05,
    y=max(daily_metrics['# of orders']) * 0.65,
    text=f"New Customers → Repeat Orders: <b style='color:{corr_color(corr_new_customers_repeat_orders)}'>{corr_new_customers_repeat_orders:.2f}</b>",
    showarrow=False,
    font=dict(color="white", size=12),
    align="left"
)

# Update layout
fig_customer_orders.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    xaxis_title='Number of New Customers',
    yaxis_title='Number of Orders',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    hovermode='closest',
    margin=dict(l=60, r=60, t=30, b=60)
)

fig_customer_orders.update_xaxes(showgrid=True, gridcolor='#2E3244')
fig_customer_orders.update_yaxes(showgrid=True, gridcolor='#2E3244')

st.plotly_chart(fig_customer_orders, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# After the New Customers vs Orders relationship section
st.markdown("<h2 style='color:white; margin-top: 40px; text-align: left;'>Sales Tactics Performance</h2>", unsafe_allow_html=True)

# Create a new container for the tactics vs revenue visualization
st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
st.markdown("<h3 style='color:white; padding: 10px;'>Sales Growth Analysis For Top Tactics</h3>", unsafe_allow_html=True)

# Aggregate data by tactic and source to get revenue contribution
tactics_data = filtered_df.groupby(['tactic', 'source']).agg({
    'attributed revenue': 'sum'
}).reset_index()

# Create a combined label for tactic and source
tactics_data['tactic_source'] = tactics_data['tactic'] + ' - ' + tactics_data['source']

# Sort by revenue and get top 5 tactic-source combinations
top_tactics = tactics_data.sort_values('attributed revenue', ascending=False).head(5)

# Calculate previous period for comparison (2 weeks ago)
two_weeks_ago_tactics = two_weeks_ago_df.groupby(['tactic', 'source']).agg({
    'attributed revenue': 'sum'
}).reset_index()

# Create the same combined label for previous period
two_weeks_ago_tactics['tactic_source'] = two_weeks_ago_tactics['tactic'] + ' - ' + two_weeks_ago_tactics['source']

# Merge current and previous period data
tactics_comparison = pd.merge(top_tactics, two_weeks_ago_tactics, 
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