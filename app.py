import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Sales Analytics Dashboard | Uichiro Yoshida",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('superstore.csv', encoding='latin-1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Month Name'] = df['Order Date'].dt.strftime('%B')
    return df

df = load_data()

# Header
st.markdown("<h1 style='text-align: center;'>📊 Sales Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Created by Uichiro Yoshida | Interactive Business Intelligence Tool</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.title("📊 Dashboard Controls")
    st.markdown("---")
    
    # Date filter
    st.subheader("📅 Time Period")
    years = sorted(df['Year'].unique())
    selected_years = st.select_slider("Select Year Range", options=years, value=(min(years), max(years)))
    
    st.markdown("---")
    
    # Region filter
    st.subheader("🌎 Region")
    all_regions = st.checkbox("All Regions", value=True)
    if all_regions:
        region = df['Region'].unique().tolist()
    else:
        region = st.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique().tolist())
    
    st.markdown("---")
    
    # Category filter
    st.subheader("📦 Category")
    all_categories = st.checkbox("All Categories", value=True)
    if all_categories:
        category = df['Category'].unique().tolist()
    else:
        category = st.multiselect("Select Category", df['Category'].unique(), default=df['Category'].unique().tolist())
    
    st.markdown("---")
    st.info("This dashboard provides comprehensive sales analytics including trends, profitability analysis, and customer insights.")

# Filter data
filtered_df = df[
    (df['Region'].isin(region)) & 
    (df['Category'].isin(category)) &
    (df['Year'] >= selected_years[0]) &
    (df['Year'] <= selected_years[1])
]

# Calculate metrics
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
total_orders = len(filtered_df)
profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

# KPI Metrics Row
st.subheader("📈 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("💰 Total Revenue", f"${total_sales:,.0f}")
col2.metric("📈 Total Profit", f"${total_profit:,.0f}")
col3.metric("🛒 Total Orders", f"{total_orders:,}")
col4.metric("📊 Profit Margin", f"{profit_margin:.1f}%")
col5.metric("💵 Avg Order Value", f"${avg_order_value:.0f}")

st.markdown("---")

# Row 1: Sales Trend and Category Breakdown
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📅 Sales Trend Over Time")
    monthly_sales = filtered_df.groupby(filtered_df['Order Date'].dt.to_period('M')).agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    monthly_sales['Order Date'] = monthly_sales['Order Date'].astype(str)
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly_sales['Order Date'],
        y=monthly_sales['Sales'],
        mode='lines+markers',
        name='Sales',
        line=dict(color='#1E88E5', width=3),
        fill='tozeroy',
        fillcolor='rgba(30, 136, 229, 0.2)'
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly_sales['Order Date'],
        y=monthly_sales['Profit'],
        mode='lines+markers',
        name='Profit',
        line=dict(color='#43A047', width=3)
    ))
    fig_trend.update_layout(
        height=400,
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.subheader("📦 Sales by Category")
    cat_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
    fig_cat = px.pie(
        cat_sales, 
        values='Sales', 
        names='Category',
        hole=0.4,
        color_discrete_sequence=['#1E88E5', '#43A047', '#FDD835']
    )
    fig_cat.update_layout(height=400)
    fig_cat.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_cat, use_container_width=True)

# Row 2: Regional Analysis and Customer Segments
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌎 Regional Performance")
    region_data = filtered_df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    fig_region = go.Figure()
    fig_region.add_trace(go.Bar(x=region_data['Region'], y=region_data['Sales'], name='Sales', marker_color='#1E88E5'))
    fig_region.add_trace(go.Bar(x=region_data['Region'], y=region_data['Profit'], name='Profit', marker_color='#43A047'))
    fig_region.update_layout(barmode='group', height=400, legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    st.subheader("👥 Customer Segments")
    segment_data = filtered_df.groupby('Segment').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    fig_segment = go.Figure()
    fig_segment.add_trace(go.Bar(x=segment_data['Segment'], y=segment_data['Sales'], name='Sales', marker_color='#5E35B1'))
    fig_segment.add_trace(go.Bar(x=segment_data['Segment'], y=segment_data['Profit'], name='Profit', marker_color='#00ACC1'))
    fig_segment.update_layout(barmode='group', height=400, legend=dict(orientation='h', yanchor='bottom', y=1.02))
    st.plotly_chart(fig_segment, use_container_width=True)

# Row 3: Profitability Analysis
st.subheader("💰 Profitability by Sub-Category")
profit_sub = filtered_df.groupby('Sub-Category')['Profit'].sum().sort_values().reset_index()
colors = ['#E53935' if x < 0 else '#43A047' for x in profit_sub['Profit']]

fig_profit = go.Figure()
fig_profit.add_trace(go.Bar(
    x=profit_sub['Profit'],
    y=profit_sub['Sub-Category'],
    orientation='h',
    marker_color=colors
))
fig_profit.update_layout(height=500)
st.plotly_chart(fig_profit, use_container_width=True)

# Row 4: Top Products and Shipping
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 Products by Revenue")
    top_products = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
    top_products['Short Name'] = top_products['Product Name'].str[:35] + '...'
    
    fig_top = px.bar(
        top_products,
        x='Sales',
        y='Short Name',
        orientation='h',
        color='Sales',
        color_continuous_scale='Blues'
    )
    fig_top.update_layout(height=400, yaxis=dict(autorange='reversed'), coloraxis_showscale=False)
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    st.subheader("🚚 Shipping Mode Analysis")
    ship_data = filtered_df.groupby('Ship Mode')['Sales'].sum().reset_index()
    
    fig_ship = px.pie(
        ship_data,
        values='Sales',
        names='Ship Mode',
        hole=0.4,
        color_discrete_sequence=['#1E88E5', '#43A047', '#FDD835', '#E53935']
    )
    fig_ship.update_layout(height=400)
    fig_ship.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_ship, use_container_width=True)

# Row 5: State Analysis
st.subheader("🗺️ Top 15 States by Sales")
state_sales = filtered_df.groupby('State')['Sales'].sum().sort_values(ascending=False).head(15).reset_index()

fig_state = px.bar(
    state_sales,
    x='State',
    y='Sales',
    color='Sales',
    color_continuous_scale='Viridis'
)
fig_state.update_layout(height=400, coloraxis_showscale=False)
st.plotly_chart(fig_state, use_container_width=True)

# Data Explorer
st.markdown("---")
st.subheader("🔍 Data Explorer")

col1, col2, col3 = st.columns(3)
col1.info(f"**Total Records:** {len(filtered_df):,}")
col2.info(f"**Date Range:** {filtered_df['Order Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Order Date'].max().strftime('%Y-%m-%d')}")
col3.info(f"**Unique Customers:** {filtered_df['Customer ID'].nunique():,}")

if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df, use_container_width=True, height=400)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.markdown("**📊 Data Source:** Sample Superstore Dataset")
col2.markdown("**🛠️ Built with:** Python, Pandas, Streamlit, Plotly")
col3.markdown("**👨‍💻 Created by:** Uichiro Yoshida")
