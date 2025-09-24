import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from PIL import Image
import base64
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Apple Market Analyzer Dashboard",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🍎 Apple Market Analyzer Dashboard</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📊 Navigation")
page = st.sidebar.selectbox(
    "Choose Analysis Section",
    ["🏠 Overview", "📈 Feature Analysis", "🔮 Predictions", "📊 Market Insights", "📋 Reports"]
)

# Load data utility functions
@st.cache_data
def load_data():
    """Load the main dataset"""
    try:
        df = pd.read_csv("Walmart_customer_fixed.csv", low_memory=False)
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'Walmart_customer_fixed.csv' is in the correct location.")
        return None

@st.cache_data
def load_apple_data():
    """Load and process Apple-specific data"""
    df = load_data()
    if df is not None:
        # Clean and process data
        df = df.drop_duplicates()
        thresh = 0.5 * df.shape[0]
        df = df.loc[:, df.isna().sum() <= thresh]
        
        # Convert common fields
        if "Purchase_Date" in df.columns:
            df["Purchase_Date"] = pd.to_datetime(df["Purchase_Date"], errors="coerce")
        if "Market_Price" in df.columns:
            df["Market_Price"] = pd.to_numeric(df["Market_Price"], errors="coerce")
        if "Purchase_Amount" in df.columns:
            df["Purchase_Amount"] = pd.to_numeric(df["Purchase_Amount"], errors="coerce")
        if "Rating" in df.columns:
            df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
        
        # Fill missing values
        if "Purchase_Amount" in df.columns:
            df["Purchase_Amount"] = df["Purchase_Amount"].fillna(1)
        
        # Filter for Apple products
        apple_df = df[df["Brand"].str.lower() == "apple"].copy()
        return df, apple_df
    return None, None

def load_summary_data():
    """Load summary data from text files"""
    summaries = {}
    summary_files = {
        'ratings': 'apple_ratings/apple_ratings_summary.txt',
        'sales': 'apple_sales/apple_sales_summary.txt',
        'price_elasticity': 'price_elasticity/price_elasticity_summary.txt',
        'product_domination': 'product_domination/product_domination_summary.txt'
    }
    
    for key, file_path in summary_files.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                summaries[key] = f.read()
        except FileNotFoundError:
            summaries[key] = f"Summary file not found: {file_path}"
    
    return summaries

def load_forecast_images():
    """Load forecast images"""
    images = {}
    image_files = {
        'ratings': 'apple_ratings/apple_ratings_forecast.png',
        'sales': 'apple_sales/apple_sales_forecast.png',
        'price_elasticity': 'price_elasticity/price_elasticity_forecast.png',
        'product_domination': 'product_domination/product_domination_forecast.png'
    }
    
    for key, file_path in image_files.items():
        try:
            if os.path.exists(file_path):
                images[key] = Image.open(file_path)
            else:
                images[key] = None
        except Exception as e:
            st.warning(f"Could not load image {file_path}: {str(e)}")
            images[key] = None
    
    return images

# Overview Page
if page == "🏠 Overview":
    st.header("📊 Dashboard Overview")
    
    # Load data
    df, apple_df = load_apple_data()
    summaries = load_summary_data()
    
    if df is not None and apple_df is not None:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📱 Total Apple Products",
                value=f"{len(apple_df):,}",
                delta=f"{len(apple_df)/len(df)*100:.1f}% of total"
            )
        
        with col2:
            avg_rating = apple_df["Rating"].mean() if "Rating" in apple_df.columns else 0
            st.metric(
                label="⭐ Average Rating",
                value=f"{avg_rating:.2f}",
                delta="Apple Products"
            )
        
        with col3:
            total_sales = apple_df["Purchase_Amount"].sum() if "Purchase_Amount" in apple_df.columns else 0
            st.metric(
                label="💰 Total Sales",
                value=f"${total_sales:,.0f}",
                delta="Apple Revenue"
            )
        
        with col4:
            avg_price = apple_df["Market_Price"].mean() if "Market_Price" in apple_df.columns else 0
            st.metric(
                label="💵 Average Price",
                value=f"${avg_price:.2f}",
                delta="Per Product"
            )
        
        st.markdown("---")
        
        # Market share visualization
        st.subheader("📈 Market Share Analysis")
        
        if "Brand" in df.columns and "Purchase_Amount" in df.columns:
            brand_share = df.groupby("Brand")["Purchase_Amount"].sum().sort_values(ascending=False)
            brand_share_pct = brand_share / brand_share.sum() * 100
            
            # Create pie chart
            fig = px.pie(
                values=brand_share_pct.values,
                names=brand_share_pct.index,
                title="Market Share by Brand",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        # Apple ratings distribution
        if "Rating" in apple_df.columns:
            st.subheader("⭐ Apple Ratings Distribution")
            fig = px.histogram(
                apple_df.dropna(subset=['Rating']),
                x='Rating',
                nbins=10,
                title="Apple Product Ratings Distribution",
                color_discrete_sequence=['#1f77b4']
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# Feature Analysis Page
elif page == "📈 Feature Analysis":
    st.header("📈 Apple Market Feature Analysis")
    
    df, apple_df = load_apple_data()
    
    if df is not None and apple_df is not None:
        # Geographic Analysis
        st.subheader("🌍 Geographic Market Insights")
        
        if "City" in apple_df.columns and "Purchase_Amount" in apple_df.columns:
            top_cities = apple_df.groupby("City")["Purchase_Amount"].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=top_cities.values,
                y=top_cities.index,
                orientation='h',
                title="Top 10 Cities by Apple Sales",
                labels={'x': 'Total Sales Amount', 'y': 'City'},
                color=top_cities.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Price vs Sales Analysis
        st.subheader("💰 Price & Sales Relationship")
        
        if "Market_Price" in apple_df.columns and "Purchase_Amount" in apple_df.columns:
            fig = px.scatter(
                apple_df,
                x="Market_Price",
                y="Purchase_Amount",
                title="Apple Price vs Purchase Volume",
                labels={'Market_Price': 'Market Price ($)', 'Purchase_Amount': 'Purchase Amount ($)'},
                color='Market_Price',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Discount Analysis
        if "Discount_Applied" in df.columns:
            st.subheader("📉 Discount Impact Analysis")
            
            disc_sales = df.groupby(["Brand", "Discount_Applied"])["Purchase_Amount"].sum().unstack(fill_value=0)
            if "Apple" in disc_sales.index:
                apple_disc = disc_sales.loc["Apple"]
                
                fig = px.bar(
                    x=apple_disc.index,
                    y=apple_disc.values,
                    title="Apple Sales: Discount vs No Discount",
                    labels={'x': 'Discount Applied', 'y': 'Total Sales Amount ($)'},
                    color=apple_disc.values,
                    color_continuous_scale=['red', 'green']
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Time-based Trends
        st.subheader("📅 Time-based Market Trends")
        
        if "Purchase_Date" in apple_df.columns and apple_df["Purchase_Date"].notna().any():
            # Monthly trends
            apple_monthly = apple_df.groupby(pd.Grouper(key="Purchase_Date", freq="M"))["Purchase_Amount"].sum()
            
            fig = px.line(
                x=apple_monthly.index,
                y=apple_monthly.values,
                title="Monthly Apple Sales Trend",
                labels={'x': 'Month', 'y': 'Sales Amount ($)'}
            )
            fig.update_traces(mode='lines+markers')
            st.plotly_chart(fig, use_container_width=True)
            
            # Weekday analysis
            apple_df_copy = apple_df.copy()
            apple_df_copy["Weekday"] = apple_df_copy["Purchase_Date"].dt.day_name()
            weekday_sales = apple_df_copy.groupby("Weekday")["Purchase_Amount"].sum().reindex(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            )
            
            fig = px.bar(
                x=weekday_sales.index,
                y=weekday_sales.values,
                title="Apple Sales by Weekday",
                labels={'x': 'Day of Week', 'y': 'Total Sales Amount ($)'},
                color=weekday_sales.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)

# Predictions Page
elif page == "🔮 Predictions":
    st.header("🔮 Apple Market Predictions")
    
    # Load forecast images and summaries
    images = load_forecast_images()
    summaries = load_summary_data()
    
    # Create tabs for different prediction types
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Ratings Forecast", "💰 Sales Forecast", "📈 Price Elasticity", "🏆 Product Domination"])
    
    with tab1:
        st.subheader("📊 Apple Ratings Forecast")
        
        if images.get('ratings'):
            st.image(images['ratings'], caption="Apple Ratings Forecast", use_column_width=True)
        
        if summaries.get('ratings'):
            st.subheader("📋 Summary")
            st.text(summaries['ratings'])
    
    with tab2:
        st.subheader("💰 Apple Sales Forecast")
        
        if images.get('sales'):
            st.image(images['sales'], caption="Apple Sales Forecast", use_column_width=True)
        
        if summaries.get('sales'):
            st.subheader("📋 Summary")
            st.text(summaries['sales'])
    
    with tab3:
        st.subheader("📈 Price Elasticity Analysis")
        
        if images.get('price_elasticity'):
            st.image(images['price_elasticity'], caption="Price Elasticity Forecast", use_column_width=True)
        
        if summaries.get('price_elasticity'):
            st.subheader("📋 Summary")
            st.text(summaries['price_elasticity'])
    
    with tab4:
        st.subheader("🏆 Product Domination Analysis")
        
        if images.get('product_domination'):
            st.image(images['product_domination'], caption="Product Domination Forecast", use_column_width=True)
        
        if summaries.get('product_domination'):
            st.subheader("📋 Summary")
            st.text(summaries['product_domination'])

# Market Insights Page
elif page == "📊 Market Insights":
    st.header("📊 Advanced Market Insights")
    
    df, apple_df = load_apple_data()
    
    if df is not None and apple_df is not None:
        # Seasonal Analysis
        st.subheader("🎯 Seasonal Sales Analysis")
        
        if "Purchase_Date" in apple_df.columns and apple_df["Purchase_Date"].notna().any():
            apple_df_copy = apple_df.copy()
            apple_df_copy["Month"] = apple_df_copy["Purchase_Date"].dt.month
            apple_df_copy["Day"] = apple_df_copy["Purchase_Date"].dt.day
            
            def label_season(row):
                m, d = row["Month"], row["Day"]
                if m == 1 and d <= 7:
                    return "New Year"
                elif m == 12 and d >= 20:
                    return "Christmas"
                elif m in [8, 9] and (m == 8 or (m == 9 and d <= 15)):
                    return "Back-to-School"
                else:
                    return "Other"
            
            apple_df_copy["Season"] = apple_df_copy.apply(label_season, axis=1)
            seasonal_sales = apple_df_copy.groupby("Season")["Purchase_Amount"].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=seasonal_sales.index,
                y=seasonal_sales.values,
                title="Apple Seasonal Sales Spikes",
                labels={'x': 'Season', 'y': 'Total Sales Amount ($)'},
                color=seasonal_sales.values,
                color_continuous_scale='Set2'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Product Category Analysis
        st.subheader("📱 Product Category Performance")
        
        if "Product_Category" in apple_df.columns:
            category_sales = apple_df.groupby("Product_Category")["Purchase_Amount"].sum().sort_values(ascending=False)
            
            fig = px.pie(
                values=category_sales.values,
                names=category_sales.index,
                title="Apple Sales by Product Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Customer Demographics (if available)
        st.subheader("👥 Customer Demographics")
        
        if "Age_Group" in apple_df.columns:
            age_sales = apple_df.groupby("Age_Group")["Purchase_Amount"].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=age_sales.index,
                y=age_sales.values,
                title="Apple Sales by Age Group",
                labels={'x': 'Age Group', 'y': 'Total Sales Amount ($)'},
                color=age_sales.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)

# Reports Page
elif page == "📋 Reports":
    st.header("📋 Analysis Reports")
    
    summaries = load_summary_data()
    
    # Create expandable sections for each report
    with st.expander("📊 Apple Ratings Analysis Report", expanded=True):
        if summaries.get('ratings'):
            st.text(summaries['ratings'])
        else:
            st.warning("Ratings summary not available")
    
    with st.expander("💰 Apple Sales Analysis Report", expanded=True):
        if summaries.get('sales'):
            st.text(summaries['sales'])
        else:
            st.warning("Sales summary not available")
    
    with st.expander("📈 Price Elasticity Analysis Report", expanded=True):
        if summaries.get('price_elasticity'):
            st.text(summaries['price_elasticity'])
        else:
            st.warning("Price elasticity summary not available")
    
    with st.expander("🏆 Product Domination Analysis Report", expanded=True):
        if summaries.get('product_domination'):
            st.text(summaries['product_domination'])
        else:
            st.warning("Product domination summary not available")
    
    # Download functionality
    st.subheader("📥 Download Reports")
    
    if st.button("📊 Generate Combined Report"):
        combined_report = ""
        for key, summary in summaries.items():
            combined_report += f"\n{'='*50}\n{key.upper()} ANALYSIS\n{'='*50}\n\n{summary}\n\n"
        
        st.download_button(
            label="📥 Download Combined Report",
            data=combined_report,
            file_name="apple_market_analysis_report.txt",
            mime="text/plain"
        )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🍎 Apple Market Analyzer Dashboard | Powered by Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
