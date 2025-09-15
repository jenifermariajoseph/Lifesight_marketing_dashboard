import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# Set page config at the beginning
st.set_page_config(layout="wide", page_title="Individual Charts")

# Inject custom CSS to hide ONLY the main app from the sidebar - MUST BE EARLY
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

# --- Custom CSS for Theming ---
def apply_custom_css():
    st.markdown("""
        <style>
        .main-container {
            padding: 0;
        }
        .main-header {
            color: #FFFFFF;
            font-size: 24px;
            text-align: left;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .sub-header {
            color: #FFFFFF;
            font-size: 18px;
            text-align: left;
            margin-bottom: 10px;
            margin-top: 20px;
        }
        .tab-content {
            padding: 10px 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1E2130;
            color: white;
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            border: none;
        }
        .stTabs [aria-selected="true"] {
            background-color: #3B4371;
            color: white;
            border-bottom: 2px solid #6366F1;
        }
        .chart-container {
            background-color: #1E2130;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #6366F1;
            text-align: center;
        }
        .metric-label {
            font-size: 14px;
            color: #FFFFFF;
            text-align: center;
        }
        .charts-row {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            width: 100%;
            gap: 20px;
        }
        .kpi-card {
            background-color: #1E2130;
            padding: 5px;
            border-radius: 10px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            height: 100%;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 10px;
        }
        .chart-title {
            color: #FFFFFF;
            font-size: 10px;
            font-weight: bold;
            margin: 0;
            padding: 0;
            text-align: center;
            width: 100%;
        }
        .chart-container {
            width: 100%;
            height: auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .chart-data {
            width: 100%;
            margin-top: 10px;
        }
        .data-container {
            flex: 1;
            order: 1; /* Place data on the left */
        }
        .chart-wrapper {
            flex: 1;
            order: 2; /* Place chart on the right */
            display: flex;
            justify-content: flex-end;
        }
        .data-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .color-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .data-text {
            color: white;
            font-size: 10px;
            margin: 0;
        }
        .plot-container {
        padding: 0;
        background-color: #1E2130;
        border-radius: 10px;
        height: 100%;
        margin-top: 10px;
    }
        </style>
    """, unsafe_allow_html=True)

# Use caching to load data only once
@st.cache_data
def load_data():
    business_df = pd.read_csv('business.csv')
    facebook_df = pd.read_csv('Facebook.csv')
    google_df = pd.read_csv('Google.csv')
    tiktok_df = pd.read_csv('TikTok.csv')

    facebook_df['source'] = 'Facebook'
    google_df['source'] = 'Google'
    tiktok_df['source'] = 'TikTok'

    marketing_df = pd.concat([facebook_df, google_df, tiktok_df])

    business_df['date'] = pd.to_datetime(business_df['date'])
    marketing_df['date'] = pd.to_datetime(marketing_df['date'])
    
    df = pd.merge(marketing_df, business_df, on='date', how='outer')
    df = df.fillna(0)
    
    return df

# Apply CSS and load data
apply_custom_css()
df = load_data()

# Get unique marketing sources (instead of companies)
sources = ['Facebook', 'Google', 'TikTok']

# Marketing source selector
selected_source = st.selectbox(
    "Select Marketing Source",
    options=sources,
    key="source_selector"
)

# Filter data for the selected marketing source
source_df = df[df['source'] == selected_source].copy()

# Calculate metrics
source_df['ctr'] = (source_df['clicks'] / source_df['impression']) * 100
source_df['cpc'] = source_df['spend'] / source_df['clicks']
source_df['roas'] = source_df['attributed revenue'] / source_df['spend']

# Custom color palette - define this BEFORE using it
CUSTOM_COLORS = ['#6366F1', '#EC4899', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#14B8A6', '#F97316']

# Define source-specific colors with simplified color schemes as requested
source_colors = {
    'Google': ['#34A853', '#34A853', '#34A853', '#34A853'],  # Google green
    'Facebook': ['#1877F2', '#1877F2', '#1877F2', '#1877F2'],  # Facebook blue
    'TikTok': ['#EE1D52', '#EE1D52', '#EE1D52', '#EE1D52']     # TikTok red
}

# Use source-specific colors or default to custom colors
CURRENT_COLORS = source_colors.get(selected_source, CUSTOM_COLORS)

# Display source header
st.markdown(f"<h1 class='main-header'>Performance Dashboard for {selected_source}</h1>", unsafe_allow_html=True)

# Add pie charts section
st.markdown("<h2 class='sub-header'>Cost Distribution</h2>", unsafe_allow_html=True)

# Prepare data for pie charts
# Donut chart for costs by region (state)
costs_by_region = source_df.groupby('state')['spend'].sum().reset_index()
total_spend_region = costs_by_region['spend'].sum()
costs_by_region['percentage'] = (costs_by_region['spend'] / total_spend_region) * 100

# Donut chart for costs by campaign name - limit to top 5
source_df['campaign_name'] = source_df['campaign'].str.replace(f"{selected_source} - ", "", regex=True)
costs_by_campaign = source_df.groupby('campaign_name')['spend'].sum().nlargest(5).reset_index()
total_spend_campaign = costs_by_campaign['spend'].sum()  # Calculate total based on top 5 only
costs_by_campaign['percentage'] = (costs_by_campaign['spend'] / total_spend_campaign) * 100

# Donut chart for costs by strategy (tactic)
costs_by_tactic = source_df.groupby('tactic')['spend'].sum().reset_index()
total_spend_tactic = costs_by_tactic['spend'].sum()
costs_by_tactic['percentage'] = (costs_by_tactic['spend'] / total_spend_tactic) * 100

# Create a function for the improved donut charts
def create_improved_donut_chart(data, values_col, names_col):
    # Sort data by value descending
    data = data.sort_values(by=values_col, ascending=False)
    
    # Get total and format for display
    total = data[values_col].sum()
    center_text = f"${int(total/1000)}k" if total >= 1000 else f"${total:,.0f}"

    # Create the donut chart
    fig = go.Figure()
    
    # Add the pie chart trace
    fig.add_trace(go.Pie(
        labels=data[names_col],
        values=data[values_col],
        hole=0.7,
        textinfo='none',
        hoverinfo='label+percent+value',
        hovertemplate='%{label}: %{percent} | $%{value:,.0f}<extra></extra>',
        marker=dict(
            colors=CUSTOM_COLORS[:len(data)],
            line=dict(color='#1E2130', width=1)
        )
    ))
    
    # Add the center text
    fig.add_annotation(
        text=center_text,
        font=dict(size=24, color='white', family='Arial, sans-serif'),
        showarrow=False,
        x=0.5,
        y=0.5
    )
    
    # Update the layout
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=180,
        width=180
    )
    
    return fig

# Create a row of columns for pie charts
cols = st.columns(3)

# Chart data definitions
chart_data = [
    ("Total Costs by Regions", costs_by_region, 'spend', 'state'),
    ("Total Costs by Campaign", costs_by_campaign, 'spend', 'campaign_name'),
    ("Total Costs by Strategy", costs_by_tactic, 'spend', 'tactic')
]

# Create each chart in its own column with KPI card styling
for i, (col, (title, data, value_col, name_col)) in enumerate(zip(cols, chart_data)):
    with col:
        # Create a container for the KPI card
        with st.container():
            # Start the KPI card container
            st.markdown(
                f"""<div class="kpi-card">
                    <h3 class="chart-title">{title}</h3>
                """,
                unsafe_allow_html=True
            )
            
            # Create two columns inside the KPI card - left for data, right for chart
            data_col, chart_col = st.columns([1, 1])
            
            # Left column for data items
            with data_col:
                # Display the data items
                data_html = "<div class='chart-data'>"
                
                # Create a table-like display for the data
                # For campaigns, show all 5 entries to match the pie chart
                max_rows = 5 if name_col == 'campaign_name' else 4
                for j, row in data.sort_values(by=value_col, ascending=False).head(max_rows).iterrows():
                    color_index = j % len(CUSTOM_COLORS)  # Ensure we don't go out of bounds
                    percentage = row['percentage']
                    value = row[value_col]
                    name = row[name_col]
                    
                    data_html += f"<div class=\"data-item\"><div class=\"color-dot\" style=\"background-color: {CUSTOM_COLORS[color_index]};\"></div><div class=\"data-text\">{name} - {percentage:.1f}% | ${value:,.0f}</div></div>"
                
                # Close the data container
                data_html += "</div>"
                st.markdown(data_html, unsafe_allow_html=True)
            
            # Right column for chart
            with chart_col:
                # Create the chart
                fig = create_improved_donut_chart(data, value_col, name_col)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Close the KPI card container
            st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
# Function to create bar charts
def create_bar_chart(data, x_col, y_col, title, color_discrete_sequence=CURRENT_COLORS):
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=color_discrete_sequence,
        text=y_col,  # Display values on bars
        template="plotly_dark"
    )
    
    # Format the text on bars based on the metric
    if 'revenue' in y_col.lower():
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='inside')
    elif 'roas' in y_col.lower():
        fig.update_traces(texttemplate='%{text:.2f}x', textposition='inside')
    elif 'ctr' in y_col.lower():
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
    elif 'cpc' in y_col.lower():
        fig.update_traces(texttemplate='$%{text:.2f}', textposition='inside')
    else:
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='inside')
    
    fig.update_layout(
        height=400,
        margin=dict(l=40, r=40, t=50, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'font': {'size': 16, 'color': 'white'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis={
            'title': None,
            'tickangle': -45 if len(data) > 5 else 0
        },
        yaxis={
            'title': None,
            'gridcolor': 'rgba(255,255,255,0.1)'
        }
    )
    
    return fig

# Create main tabs for different metrics
main_tabs = st.tabs(["Revenue", "ROAS", "CTR", "CPC"])

# 1. REVENUE TAB
with main_tabs[0]:
    revenue_tabs = st.tabs(["By Region", "By Campaign", "By Strategy"])
    
    # Revenue by Region
    with revenue_tabs[0]:
        revenue_by_region = source_df.groupby('state')['attributed revenue'].sum().reset_index()
        revenue_by_region = revenue_by_region.sort_values('attributed revenue', ascending=False)
        
        st.plotly_chart(
            create_bar_chart(
                revenue_by_region, 
                'state', 
                'attributed revenue', 
                f"Revenue by Region for {selected_source}"
            ),
            use_container_width=True
        )
    
    # Revenue by Campaign
    with revenue_tabs[1]:
        revenue_by_campaign = source_df.groupby('campaign_name')['attributed revenue'].sum().reset_index()
        revenue_by_campaign = revenue_by_campaign.sort_values('attributed revenue', ascending=False)
        
        st.plotly_chart(
            create_bar_chart(
                revenue_by_campaign, 
                'campaign_name', 
                'attributed revenue', 
                f"Revenue by Campaign for {selected_source}"
            ),
            use_container_width=True
        )
    
    # Revenue by Strategy
    with revenue_tabs[2]:
        revenue_by_strategy = source_df.groupby('tactic')['attributed revenue'].sum().reset_index()
        revenue_by_strategy = revenue_by_strategy.sort_values('attributed revenue', ascending=False)
        
        st.plotly_chart(
            create_bar_chart(
                revenue_by_strategy, 
                'tactic', 
                'attributed revenue', 
                f"Revenue by Strategy for {selected_source}"
            ),
            use_container_width=True
        )

# 2. ROAS TAB
with main_tabs[1]:
    roas_tabs = st.tabs(["By Region", "By Campaign", "By Strategy"])
    
    # ROAS by Region
    with roas_tabs[0]:
        roas_by_region = source_df.groupby('state').agg({
            'attributed revenue': 'sum',
            'spend': 'sum'
        }).reset_index()
        roas_by_region['roas'] = roas_by_region['attributed revenue'] / roas_by_region['spend']
        roas_by_region = roas_by_region.sort_values('roas', ascending=False)
        
        st.plotly_chart(
            create_bar_chart(
                roas_by_region, 
                'state', 
                'roas', 
                f"ROAS by Region for {selected_source}"
            ),
            use_container_width=True
        )
    
    # ROAS by Campaign
    with roas_tabs[1]:
        roas_by_campaign = source_df.groupby('campaign_name').agg({
            'attributed revenue': 'sum',
            'spend': 'sum'
        }).reset_index()
        roas_by_campaign['roas'] = roas_by_campaign['attributed revenue'] / roas_by_campaign['spend']
        roas_by_campaign = roas_by_campaign.sort_values('roas', ascending=False)
        
        st.plotly_chart(
            create_bar_chart(
                roas_by_campaign, 
                'campaign_name', 
                'roas', 
                f"ROAS by Campaign for {selected_source}"
            ),
            use_container_width=True
        )
    
    # ROAS by Strategy
    with roas_tabs[2]:
        roas_by_strategy = source_df.groupby('tactic').agg({
            'attributed revenue': 'sum',
            'spend': 'sum'
        }).reset_index()
        roas_by_strategy['roas'] = roas_by_strategy['attributed revenue'] / roas_by_strategy['spend']
        roas_by_strategy = roas_by_strategy.sort_values('roas', ascending=False)
        
        st.plotly_chart(
            create_bar_chart(
                roas_by_strategy, 
                'tactic', 
                'roas', 
                f"ROAS by Strategy for {selected_source}"
            ),
            use_container_width=True
        )

# 3. CTR TAB
with main_tabs[2]:
    ctr_tabs = st.tabs(["By Region", "By Campaign", "By Strategy"])
    
    # CTR by Region
    with ctr_tabs[0]:
        ctr_by_region = source_df.groupby('state').agg({
            'clicks': 'sum',
            'impression': 'sum'
        }).reset_index()
        ctr_by_region['ctr'] = (ctr_by_region['clicks'] / ctr_by_region['impression']) * 100
        ctr_by_region = ctr_by_region.sort_values('ctr', ascending=False)
        
        st.plotly_chart(
            create_bar_chart(
                ctr_by_region, 
                'state', 
                'ctr', 
                f"CTR by Region for {selected_source}"
            ),
            use_container_width=True
        )
    
    # CTR by Campaign
    with ctr_tabs[1]:
        ctr_by_campaign = source_df.groupby('campaign_name').agg({
            'clicks': 'sum',
            'impression': 'sum'
        }).reset_index()
        ctr_by_campaign['ctr'] = (ctr_by_campaign['clicks'] / ctr_by_campaign['impression']) * 100
        ctr_by_campaign = ctr_by_campaign.sort_values('ctr', ascending=False)
        
        st.plotly_chart(
            create_bar_chart(
                ctr_by_campaign, 
                'campaign_name', 
                'ctr', 
                f"CTR by Campaign for {selected_source}"
            ),
            use_container_width=True
        )
    
    # CTR by Strategy
    with ctr_tabs[2]:
        ctr_by_strategy = source_df.groupby('tactic').agg({
            'clicks': 'sum',
            'impression': 'sum'
        }).reset_index()
        ctr_by_strategy['ctr'] = (ctr_by_strategy['clicks'] / ctr_by_strategy['impression']) * 100
        ctr_by_strategy = ctr_by_strategy.sort_values('ctr', ascending=False)
        
        st.plotly_chart(
            create_bar_chart(
                ctr_by_strategy, 
                'tactic', 
                'ctr', 
                f"CTR by Strategy for {selected_source}"
            ),
            use_container_width=True
        )

# 4. CPC TAB
with main_tabs[3]:
    cpc_tabs = st.tabs(["By Region", "By Campaign", "By Strategy"])
    
    # CPC by Region
    with cpc_tabs[0]:
        cpc_by_region = source_df.groupby('state').agg({
            'spend': 'sum',
            'clicks': 'sum'
        }).reset_index()
        cpc_by_region['cpc'] = cpc_by_region['spend'] / cpc_by_region['clicks']
        cpc_by_region = cpc_by_region.sort_values('cpc', ascending=True)  # Lower CPC is better
        
        st.plotly_chart(
            create_bar_chart(
                cpc_by_region, 
                'state', 
                'cpc', 
                f"CPC by Region for {selected_source}"
            ),
            use_container_width=True
        )
    
    # CPC by Campaign
    with cpc_tabs[1]:
        cpc_by_campaign = source_df.groupby('campaign_name').agg({
            'spend': 'sum',
            'clicks': 'sum'
        }).reset_index()
        cpc_by_campaign['cpc'] = cpc_by_campaign['spend'] / cpc_by_campaign['clicks']
        cpc_by_campaign = cpc_by_campaign.sort_values('cpc', ascending=True)  # Lower CPC is better
        
        st.plotly_chart(
            create_bar_chart(
                cpc_by_campaign, 
                'campaign_name', 
                'cpc', 
                f"CPC by Campaign for {selected_source}"
            ),
            use_container_width=True
        )
    
    # CPC by Strategy
    with cpc_tabs[2]:
        cpc_by_strategy = source_df.groupby('tactic').agg({
            'spend': 'sum',
            'clicks': 'sum'
        }).reset_index()
        cpc_by_strategy['cpc'] = cpc_by_strategy['spend'] / cpc_by_strategy['clicks']
        cpc_by_strategy = cpc_by_strategy.sort_values('cpc', ascending=True)  # Lower CPC is better
        
        st.plotly_chart(
            create_bar_chart(
                cpc_by_strategy, 
                'tactic', 
                'cpc', 
                f"CPC by Strategy for {selected_source}"
            ),
            use_container_width=True
        )