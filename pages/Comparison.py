
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config at the beginning (only once)
st.set_page_config(layout="wide", page_title="Comparitative Performance")

# Inject custom CSS to hide ONLY the main app from the sidebar - MOVED UP
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
            font-size: 12px;
            text-align: left;
            margin-bottom: 5px;
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
            color: #FFFFFF; /* Changed to white for better visibility */
            font-size: 10px; /* Reduced from 18px */
            font-weight: bold;
            margin: 0;
            padding: 0;
            text-align: center;
            width: 100%;
        }
        .chart-subtitle {
            color: #A3A8B8; /* Swapped with title color */
            font-size: 10px;
            margin: 0;
            padding: 0;
            margin-bottom: 10px;
            text-align: center;
            width: 100%
            font-size: 12px;
            margin: 0;
            padding: 0;
            margin-bottom: 15px;
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
        /* Add new flex layout for chart and data */
        .chart-and-data {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            gap: 10px; /* Small gap between elements */
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
        .stSelectbox > div > div > div {
            background-color: #1E2130;
            color: white;
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

# Remove the pie chart selector and related code
# Delete these lines (channel selector for pie charts)
# pie_chart_channel = st.selectbox(
#     "Select Channel for Pie Charts",
#     options=df['source'].unique(),
#     key="pie_chart_channel_selector"
# )

# # Filter data for the selected channel for the pie charts
# pie_chart_df = df[df['source'] == pie_chart_channel].copy()

# # Custom color palette for the donut charts
# CUSTOM_COLORS = ['#6366F1', '#EC4899', '#8B5CF6', '#10B981', '#F59E0B']

# # Donut chart for costs by region (state)
# costs_by_region = pie_chart_df.groupby('state')['spend'].sum().reset_index()
# total_spend_region = costs_by_region['spend'].sum()
# costs_by_region['percentage'] = (costs_by_region['spend'] / total_spend_region) * 100

# # Donut chart for costs by campaign name - limit to top 5
# costs_by_campaign = pie_chart_df.groupby('campaign')['spend'].sum().nlargest(5).reset_index()
# total_spend_campaign = costs_by_campaign['spend'].sum()  # Calculate total based on top 5 only
# costs_by_campaign['percentage'] = (costs_by_campaign['spend'] / total_spend_campaign) * 100

# # Donut chart for costs by strategy (tactic)
# costs_by_tactic = pie_chart_df.groupby('tactic')['spend'].sum().reset_index()
# total_spend_tactic = costs_by_tactic['spend'].sum()
# costs_by_tactic['percentage'] = (costs_by_tactic['spend'] / total_spend_tactic) * 100

# # Create a function for the improved donut charts
# def create_improved_donut_chart(data, values_col, names_col):
#     # Sort data by value descending
#     data = data.sort_values(by=values_col, ascending=False)
    
#     # Get total and format for display
#     total = data[values_col].sum()
#     center_text = f"${int(total/1000)}k" if total >= 1000 else f"${total:,.0f}"

#     # Create the donut chart
#     fig = go.Figure()
    
#     # Add the pie chart trace
#     fig.add_trace(go.Pie(
#         labels=data[names_col],
#         values=data[values_col],
#         hole=0.7,
#         textinfo='none',
#         hoverinfo='label+percent+value',
#         hovertemplate='%{label}: %{percent} | $%{value:,.0f}<extra></extra>',
#         marker=dict(
#             colors=CUSTOM_COLORS[:len(data)],
#             line=dict(color='#1E2130', width=1)
#         )
#     ))
    
#     # Add the center text
#     fig.add_annotation(
#         text=center_text,
#         font=dict(size=24, color='white', family='Arial, sans-serif'),
#         showarrow=False,
#         x=0.5,
#         y=0.5
#     )
    
#     # Update the layout
#     fig.update_layout(
#         showlegend=False,
#         margin=dict(t=0, b=0, l=0, r=0),
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor='rgba(0,0,0,0)',
#         height=180,
#         width=180
#     )
    
#     return fig

# # Display charts in a single row
# st.markdown("<h1 class='main-header'>Marketing Cost Breakdowns</h1>", unsafe_allow_html=True)

# # Create a row of columns using Streamlit's native column layout
# cols = st.columns(3)

# # Chart data definitions
# chart_data = [
#     ("Total Costs by Regions", costs_by_region, 'spend', 'state'),
#     ("Total Costs by Campaign", costs_by_campaign, 'spend', 'campaign'),
#     ("Total Costs by Strategy", costs_by_tactic, 'spend', 'tactic')
# ]

# # Create each chart in its own column with KPI card styling
# for i, (col, (title, data, value_col, name_col)) in enumerate(zip(cols, chart_data)):
#     with col:
#         # Create a container for the KPI card
#         with st.container():
#             # Start the KPI card container
#             st.markdown(
#                 f"""<div class="kpi-card">
#                     <h3 class="chart-title">{title}</h3>
#                 """,
#                 unsafe_allow_html=True
#             )
            
#             # Create two columns inside the KPI card - left for data, right for chart
#             data_col, chart_col = st.columns([1, 1])
            
#             # Left column for data items
#             with data_col:
#                 # Display the data items
#                 data_html = "<div class='chart-data'>"
                
#                 # Create a table-like display for the data
#                 # For campaigns, show all 5 entries to match the pie chart
#                 max_rows = 5 if name_col == 'campaign' else 4
#                 for j, row in data.sort_values(by=value_col, ascending=False).head(max_rows).iterrows():
#                     color_index = j % len(CUSTOM_COLORS)  # Ensure we don't go out of bounds
#                     percentage = row['percentage']
#                     value = row[value_col]
#                     name = row[name_col]
                    
#                     # Fixed indentation and removed extra whitespace
#                     data_html += f"<div class=\"data-item\"><div class=\"color-dot\" style=\"background-color: {CUSTOM_COLORS[color_index]};\">\"></div><div class=\"data-text\">{name} - {percentage:.1f}% | ${value:,.0f}</div></div>"
                
#                 # Close the data container
#                 data_html += "</div>"
#                 st.markdown(data_html, unsafe_allow_html=True)
            
#             # Right column for chart
#             with chart_col:
#                 # Create the chart
#                 fig = create_improved_donut_chart(data, value_col, name_col)
#                 st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
#             # Close the KPI card container
#             st.markdown("</div>", unsafe_allow_html=True)

# # Add some spacing between sections
# st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# Create a line chart comparing income from different platforms over time
st.markdown("<h1 class='main-header'>Platform Comparison</h1>", unsafe_allow_html=True)

# Prepare data for the line chart - aggregate by date and source
platform_income_by_date = df.groupby(['date', 'source'])['attributed revenue'].sum().reset_index()

# Filter data for August and September only
platform_income_by_date['month'] = platform_income_by_date['date'].dt.month
platform_income_by_date['year'] = platform_income_by_date['date'].dt.year
platform_income_by_date_filtered = platform_income_by_date[
    ((platform_income_by_date['month'] == 8) | (platform_income_by_date['month'] == 9)) & 
    (platform_income_by_date['year'] == 2025)
].copy()

# Calculate ROAS (Return on Ad Spend) by date and source
platform_roas_by_date = df.groupby(['date', 'source']).apply(lambda x: x['attributed revenue'].sum() / x['spend'].sum()).reset_index(name='roas')

# Aggregate data by source for the bar chart
platform_income = df.groupby('source')['attributed revenue'].sum().reset_index()
platform_spend = df.groupby('source')['spend'].sum().reset_index()

# Calculate comprehensive attribution metrics for each platform
platform_attribution = df.groupby('source').apply(lambda x: {
    'revenue': x['attributed revenue'].sum(),
    'spend': x['spend'].sum(),
    'impressions': x['impression'].sum(),
    'clicks': x['clicks'].sum(),
    'roas': x['attributed revenue'].sum() / x['spend'].sum(),
    'ctr': (x['clicks'].sum() / x['impression'].sum()) * 100,  # Click-through rate as percentage
    'cpc': x['spend'].sum() / x['clicks'].sum()  # Cost per click
}).reset_index(name='metrics')

# Extract the metrics into separate columns
platform_attribution['revenue'] = platform_attribution['metrics'].apply(lambda x: x['revenue'])
platform_attribution['spend'] = platform_attribution['metrics'].apply(lambda x: x['spend'])
platform_attribution['impressions'] = platform_attribution['metrics'].apply(lambda x: x['impressions'])
platform_attribution['clicks'] = platform_attribution['metrics'].apply(lambda x: x['clicks'])
platform_attribution['roas'] = platform_attribution['metrics'].apply(lambda x: x['roas'])
platform_attribution['ctr'] = platform_attribution['metrics'].apply(lambda x: x['ctr'])
platform_attribution['cpc'] = platform_attribution['metrics'].apply(lambda x: x['cpc'])

# Open the plot container div with the CSS class
st.markdown("<div class='plot-container'>", unsafe_allow_html=True)

# Define specific colors for each platform
# Define CUSTOM_COLORS first since it's referenced later
CUSTOM_COLORS = ['#6366F1', '#EC4899', '#8B5CF6', '#10B981', '#F59E0B']

CUSTOM_PLATFORM_COLORS = {
    'Facebook': '#1877F2',  # Facebook blue
    'Google': '#34A853',    # Google green
    'TikTok': '#FF0050'     # TikTok red
}

# Create two columns for the charts
col1, col2 = st.columns(2)

with col2:  # Changed from col1 to col2
    # Create a single line of percentages for display above the chart
    percentage_text = ""
    for i, row in platform_attribution.iterrows():
        source = row['source']
        color = CUSTOM_PLATFORM_COLORS.get(source, CUSTOM_COLORS[i % len(CUSTOM_COLORS)])
        total_revenue = row['revenue']
        
        # Calculate percentage of total across all platforms
        percentage = (total_revenue / platform_attribution['revenue'].sum()) * 100
        
        # Add to the percentage text with colored source name
        percentage_text += f"<span style='color:{color}'><b>{source}</b>: {percentage:.1f}%</span>   "
    
    # Display the percentage line above the chart
    st.markdown(f"<div style='text-align: center; padding: 5px; background-color: rgba(0,0,0,0.3); margin-bottom: 10px; border-radius: 5px;'>{percentage_text}</div>", unsafe_allow_html=True)
    
    # Create the line chart with date on x-axis and income on y-axis for Aug-Sep only
    fig_line = px.line(
        platform_income_by_date_filtered,
        x='date',
        y='attributed revenue',
        color='source',
        markers=True,  # Add markers to the line
        color_discrete_map=CUSTOM_PLATFORM_COLORS,  # Use our custom color mapping
        labels={'attributed revenue': 'Total Income ($)', 'date': 'Date', 'source': 'Platform'},
        title='Income Over Time (August-September 2025)',
        line_shape='spline'  # Use spline interpolation for smoother curves
    )

    # Customize the layout
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title=dict(font=dict(size=16)), 
            tickfont=dict(size=14),
            showgrid=False,  # Remove x-axis grid for cleaner look
            range=[platform_income_by_date_filtered['date'].min() - pd.Timedelta(days=2),  # Add padding to x-axis
                   platform_income_by_date_filtered['date'].max() + pd.Timedelta(days=2)]
        ),
        yaxis=dict(
            title=dict(font=dict(size=16)), 
            tickfont=dict(size=14), 
            gridcolor='rgba(255,255,255,0.05)',  # Lighter grid lines
            showgrid=True
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        height=500,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            bgcolor='rgba(0,0,0,0)',  # Transparent legend background
            font=dict(size=12, color='white')
        ),
        hovermode='x unified'  # Show all values at the same x-position on hover
    )

    # Format the y-axis to show dollar amounts
    fig_line.update_yaxes(tickprefix='$', tickformat=',.')

    # Add value labels on the markers but only at key points to avoid clutter
    # Get every 3rd point to reduce label density
    for trace in fig_line.data:
        y_vals = trace.y
        # Fix the formatting error - use proper string formatting with f-strings
        text_vals = [f"${int(val):,}" if i % 3 == 0 else '' for i, val in enumerate(y_vals)]
        trace.update(
            texttemplate='%{text}',
            text=text_vals,
            textposition='top center',
            textfont=dict(size=12, color='white'),
            line=dict(width=4, shape='spline', smoothing=1.3),  # Thicker lines for better visibility
            marker=dict(size=10, opacity=0.9)  # Larger markers for better visibility
        )

    # Display the line chart
    st.plotly_chart(fig_line, use_container_width=True)

with col1:  # Changed from col2 to col1
    # Create tabs for different metrics
    tab1, tab2, tab3, tab4 = st.tabs(["Revenue", "ROAS", "CTR", "CPC"])
    
    with tab1:
        # Create a dataframe for Revenue visualization
        platform_revenue = platform_attribution[['source', 'revenue']].sort_values(by='revenue', ascending=True)
        
        # Create horizontal bar chart for Revenue
        fig_bar_revenue = px.bar(
            platform_revenue,
            y='source',
            x='revenue',
            orientation='h',
            color='source',
            color_discrete_map=CUSTOM_PLATFORM_COLORS,
            labels={'revenue': 'Revenue ($)', 'source': 'Platform'},
            title='Revenue by Platform'
        )
        
        # Customize the layout
        fig_bar_revenue.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(title=dict(font=dict(size=16)), tickfont=dict(size=14)),
            yaxis=dict(title=dict(font=dict(size=16)), tickfont=dict(size=14)),
            margin=dict(l=40, r=40, t=40, b=40),
            height=500,
            showlegend=False
        )
        
        # Add value labels on the bars
        fig_bar_revenue.update_traces(
            texttemplate='%{x:$,.0f}',  # Use Plotly's built-in formatting
            textposition='outside',
            textfont=dict(size=14, color='white'),
            marker_line_width=0
        )
        
        # Display the chart
        st.plotly_chart(fig_bar_revenue, use_container_width=True)
    
    with tab2:
        # Create a dataframe for ROAS visualization
        platform_roas = platform_attribution[['source', 'roas']].sort_values(by='roas', ascending=True)
        
        # Create horizontal bar chart for ROAS
        fig_bar_roas = px.bar(
            platform_roas,
            y='source',
            x='roas',
            orientation='h',
            color='source',
            color_discrete_map=CUSTOM_PLATFORM_COLORS,
            labels={'roas': 'Return on Ad Spend (ROAS)', 'source': 'Platform'},
            title='ROAS by Platform (Revenue/Spend)'
        )
        
        # Customize the layout
        fig_bar_roas.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(title=dict(font=dict(size=16)), tickfont=dict(size=14)),
            yaxis=dict(title=dict(font=dict(size=16)), tickfont=dict(size=14)),
            margin=dict(l=40, r=40, t=40, b=40),
            height=500,
            showlegend=False
        )
        
        # Add value labels on the bars
        fig_bar_roas.update_traces(
            texttemplate='%{x:.2f}x',
            textposition='outside',
            textfont=dict(size=14, color='white'),
            marker_line_width=0
        )
        
        # Display the chart
        st.plotly_chart(fig_bar_roas, use_container_width=True)
    
    with tab3:
        # Create a dataframe for CTR visualization
        platform_ctr = platform_attribution[['source', 'ctr']].sort_values(by='ctr', ascending=True)
        
        # Create horizontal bar chart for CTR
        fig_bar_ctr = px.bar(
            platform_ctr,
            y='source',
            x='ctr',
            orientation='h',
            color='source',
            color_discrete_map=CUSTOM_PLATFORM_COLORS,
            labels={'ctr': 'Click-Through Rate (%)', 'source': 'Platform'},
            title='CTR by Platform (Clicks/Impressions)'
        )
        
        # Customize the layout
        fig_bar_ctr.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(title=dict(font=dict(size=16)), tickfont=dict(size=14)),
            yaxis=dict(title=dict(font=dict(size=16)), tickfont=dict(size=14)),
            margin=dict(l=40, r=40, t=40, b=40),
            height=500,
            showlegend=False
        )
        
        # Add value labels on the bars
        fig_bar_ctr.update_traces(
            texttemplate='%{x:.2f}%',
            textposition='outside',
            textfont=dict(size=14, color='white'),
            marker_line_width=0
        )
        
        # Display the chart
        st.plotly_chart(fig_bar_ctr, use_container_width=True)
    
    with tab4:
        # Create a dataframe for CPC visualization
        platform_cpc = platform_attribution[['source', 'cpc']].sort_values(by='cpc', ascending=True)
        
        # Create horizontal bar chart for CPC
        fig_bar_cpc = px.bar(
            platform_cpc,
            y='source',
            x='cpc',
            orientation='h',
            color='source',
            color_discrete_map=CUSTOM_PLATFORM_COLORS,
            labels={'cpc': 'Cost Per Click ($)', 'source': 'Platform'},
            title='CPC by Platform (Spend/Clicks)'
        )
        
        # Customize the layout
        fig_bar_cpc.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(title=dict(font=dict(size=16)), tickfont=dict(size=14)),
            yaxis=dict(title=dict(font=dict(size=16)), tickfont=dict(size=14)),
            margin=dict(l=40, r=40, t=40, b=40),
            height=500,
            showlegend=False
        )
        
        # Format the x-axis to show dollar amounts
        fig_bar_cpc.update_xaxes(tickprefix='$', tickformat=',.')
        
        # Add value labels on the bars
        fig_bar_cpc.update_traces(
            texttemplate='%{x:$,.00f}',  # Changed from '${:,.0f}' to '%{x:$,.0f}'
            textposition='outside',
            textfont=dict(size=14, color='white'),
            marker_line_width=0
        )
        
        # Display the chart
        st.plotly_chart(fig_bar_cpc, use_container_width=True)

# Close the plot container
st.markdown("</div>", unsafe_allow_html=True)

# Add spacing
st.markdown("<br><br>", unsafe_allow_html=True)

# Create campaign metrics for top income streams by ROAS
st.markdown("<h1 class='main-header'>Top and Bottom Income Streams by ROAS</h1>", unsafe_allow_html=True)

# Create tabs for each platform
tabs = st.tabs(["Facebook", "Google", "TikTok"])

# Process each platform in its respective tab
for i, platform in enumerate(["Facebook", "Google", "TikTok"]):
    with tabs[i]:
        # Filter data for the current platform
        platform_df = df[df['source'] == platform]
        
        if len(platform_df) > 0:
            # Calculate metrics by campaign for this platform
            platform_campaign_metrics = platform_df.groupby('campaign').agg({
                'spend': 'sum',
                'attributed revenue': 'sum',
                'clicks': 'sum',
                'impression': 'sum'
            }).reset_index()
            
            # Calculate ROAS and other metrics
            platform_campaign_metrics['ROAS'] = platform_campaign_metrics['attributed revenue'] / platform_campaign_metrics['spend']
            platform_campaign_metrics['CTR'] = (platform_campaign_metrics['clicks'] / platform_campaign_metrics['impression']) * 100
            platform_campaign_metrics['CPC'] = platform_campaign_metrics['spend'] / platform_campaign_metrics['clicks']
            
            # Format metrics for display
            platform_campaign_metrics['ROAS'] = platform_campaign_metrics['ROAS'].round(2)
            platform_campaign_metrics['CTR'] = platform_campaign_metrics['CTR'].round(2).astype(str) + '%'
            platform_campaign_metrics['CPC'] = '$' + platform_campaign_metrics['CPC'].round(2).astype(str)
            platform_campaign_metrics['spend'] = '$' + platform_campaign_metrics['spend'].round(2).astype(str)
            platform_campaign_metrics['attributed revenue'] = '$' + platform_campaign_metrics['attributed revenue'].round(2).astype(str)
            
            # Get top 5 and bottom 5 campaigns by ROAS
            top_campaigns_by_roas = platform_campaign_metrics.nlargest(5, 'ROAS')
            bottom_campaigns_by_roas = platform_campaign_metrics.nsmallest(5, 'ROAS')
            
            # Display top and bottom 5 campaigns side by side
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"🏆 Top 5 Campaigns by ROAS")
                st.dataframe(top_campaigns_by_roas[['campaign', 'ROAS', 'attributed revenue', 'spend', 'CTR', 'CPC']], use_container_width=True)
            
            with col2:
                st.subheader(f"⚠️ Bottom 5 Campaigns by ROAS")
                st.dataframe(bottom_campaigns_by_roas[['campaign', 'ROAS', 'attributed revenue', 'spend', 'CTR', 'CPC']], use_container_width=True)
        else:
            st.info(f"No data available for {platform}")

