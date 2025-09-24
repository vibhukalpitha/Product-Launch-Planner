"""
Utility functions for the Apple Market Analyzer Dashboard
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from PIL import Image
import streamlit as st

def load_and_clean_data(file_path="Walmart_customer_fixed.csv"):
    """
    Load and clean the main dataset
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        tuple: (full_dataframe, apple_dataframe)
    """
    try:
        df = pd.read_csv(file_path, low_memory=False)
        
        # Drop duplicates
        df = df.drop_duplicates()
        
        # Drop mostly empty columns (>50% NA)
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
        
    except FileNotFoundError:
        st.error(f"Data file not found: {file_path}")
        return None, None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def create_market_share_chart(df):
    """
    Create market share pie chart
    
    Args:
        df (pd.DataFrame): Main dataframe
        
    Returns:
        plotly.graph_objects.Figure: Market share pie chart
    """
    if "Brand" not in df.columns or "Purchase_Amount" not in df.columns:
        return None
    
    brand_share = df.groupby("Brand")["Purchase_Amount"].sum().sort_values(ascending=False)
    brand_share_pct = brand_share / brand_share.sum() * 100
    
    fig = px.pie(
        values=brand_share_pct.values,
        names=brand_share_pct.index,
        title="Market Share by Brand",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_ratings_distribution(apple_df):
    """
    Create ratings distribution histogram
    
    Args:
        apple_df (pd.DataFrame): Apple-specific dataframe
        
    Returns:
        plotly.graph_objects.Figure: Ratings distribution chart
    """
    if "Rating" not in apple_df.columns:
        return None
    
    fig = px.histogram(
        apple_df.dropna(subset=['Rating']),
        x='Rating',
        nbins=10,
        title="Apple Product Ratings Distribution",
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(showlegend=False)
    return fig

def create_geographic_analysis(apple_df):
    """
    Create geographic sales analysis
    
    Args:
        apple_df (pd.DataFrame): Apple-specific dataframe
        
    Returns:
        plotly.graph_objects.Figure: Geographic sales chart
    """
    if "City" not in apple_df.columns or "Purchase_Amount" not in apple_df.columns:
        return None
    
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
    return fig

def create_price_sales_scatter(apple_df):
    """
    Create price vs sales scatter plot
    
    Args:
        apple_df (pd.DataFrame): Apple-specific dataframe
        
    Returns:
        plotly.graph_objects.Figure: Price vs sales scatter plot
    """
    if "Market_Price" not in apple_df.columns or "Purchase_Amount" not in apple_df.columns:
        return None
    
    fig = px.scatter(
        apple_df,
        x="Market_Price",
        y="Purchase_Amount",
        title="Apple Price vs Purchase Volume",
        labels={'Market_Price': 'Market Price ($)', 'Purchase_Amount': 'Purchase Amount ($)'},
        color='Market_Price',
        color_continuous_scale='Viridis'
    )
    return fig

def create_discount_analysis(df):
    """
    Create discount impact analysis
    
    Args:
        df (pd.DataFrame): Main dataframe
        
    Returns:
        plotly.graph_objects.Figure: Discount analysis chart
    """
    if "Discount_Applied" not in df.columns or "Brand" not in df.columns or "Purchase_Amount" not in df.columns:
        return None
    
    disc_sales = df.groupby(["Brand", "Discount_Applied"])["Purchase_Amount"].sum().unstack(fill_value=0)
    if "Apple" not in disc_sales.index:
        return None
    
    apple_disc = disc_sales.loc["Apple"]
    
    fig = px.bar(
        x=apple_disc.index,
        y=apple_disc.values,
        title="Apple Sales: Discount vs No Discount",
        labels={'x': 'Discount Applied', 'y': 'Total Sales Amount ($)'},
        color=apple_disc.values,
        color_continuous_scale=['red', 'green']
    )
    return fig

def create_monthly_trends(apple_df):
    """
    Create monthly sales trends
    
    Args:
        apple_df (pd.DataFrame): Apple-specific dataframe
        
    Returns:
        plotly.graph_objects.Figure: Monthly trends chart
    """
    if "Purchase_Date" not in apple_df.columns or "Purchase_Amount" not in apple_df.columns:
        return None
    
    if apple_df["Purchase_Date"].notna().any():
        apple_monthly = apple_df.groupby(pd.Grouper(key="Purchase_Date", freq="M"))["Purchase_Amount"].sum()
        
        fig = px.line(
            x=apple_monthly.index,
            y=apple_monthly.values,
            title="Monthly Apple Sales Trend",
            labels={'x': 'Month', 'y': 'Sales Amount ($)'}
        )
        fig.update_traces(mode='lines+markers')
        return fig
    return None

def create_weekday_analysis(apple_df):
    """
    Create weekday sales analysis
    
    Args:
        apple_df (pd.DataFrame): Apple-specific dataframe
        
    Returns:
        plotly.graph_objects.Figure: Weekday analysis chart
    """
    if "Purchase_Date" not in apple_df.columns or "Purchase_Amount" not in apple_df.columns:
        return None
    
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
    return fig

def create_seasonal_analysis(apple_df):
    """
    Create seasonal sales analysis
    
    Args:
        apple_df (pd.DataFrame): Apple-specific dataframe
        
    Returns:
        plotly.graph_objects.Figure: Seasonal analysis chart
    """
    if "Purchase_Date" not in apple_df.columns or "Purchase_Amount" not in apple_df.columns:
        return None
    
    if not apple_df["Purchase_Date"].notna().any():
        return None
    
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
    return fig

def create_category_analysis(apple_df):
    """
    Create product category analysis
    
    Args:
        apple_df (pd.DataFrame): Apple-specific dataframe
        
    Returns:
        plotly.graph_objects.Figure: Category analysis chart
    """
    if "Product_Category" not in apple_df.columns or "Purchase_Amount" not in apple_df.columns:
        return None
    
    category_sales = apple_df.groupby("Product_Category")["Purchase_Amount"].sum().sort_values(ascending=False)
    
    fig = px.pie(
        values=category_sales.values,
        names=category_sales.index,
        title="Apple Sales by Product Category",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    return fig

def create_age_group_analysis(apple_df):
    """
    Create age group analysis
    
    Args:
        apple_df (pd.DataFrame): Apple-specific dataframe
        
    Returns:
        plotly.graph_objects.Figure: Age group analysis chart
    """
    if "Age_Group" not in apple_df.columns or "Purchase_Amount" not in apple_df.columns:
        return None
    
    age_sales = apple_df.groupby("Age_Group")["Purchase_Amount"].sum().sort_values(ascending=False)
    
    fig = px.bar(
        x=age_sales.index,
        y=age_sales.values,
        title="Apple Sales by Age Group",
        labels={'x': 'Age Group', 'y': 'Total Sales Amount ($)'},
        color=age_sales.values,
        color_continuous_scale='Blues'
    )
    return fig

def load_summary_data():
    """
    Load summary data from text files
    
    Returns:
        dict: Dictionary containing summary data
    """
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
    """
    Load forecast images
    
    Returns:
        dict: Dictionary containing PIL Image objects
    """
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
            print(f"Could not load image {file_path}: {str(e)}")
            images[key] = None
    
    return images

def calculate_key_metrics(df, apple_df):
    """
    Calculate key metrics for the dashboard
    
    Args:
        df (pd.DataFrame): Main dataframe
        apple_df (pd.DataFrame): Apple-specific dataframe
        
    Returns:
        dict: Dictionary containing key metrics
    """
    metrics = {}
    
    if df is not None and apple_df is not None:
        metrics['total_apple_products'] = len(apple_df)
        metrics['apple_percentage'] = len(apple_df) / len(df) * 100 if len(df) > 0 else 0
        
        if "Rating" in apple_df.columns:
            metrics['avg_rating'] = apple_df["Rating"].mean()
        else:
            metrics['avg_rating'] = 0
        
        if "Purchase_Amount" in apple_df.columns:
            metrics['total_sales'] = apple_df["Purchase_Amount"].sum()
        else:
            metrics['total_sales'] = 0
        
        if "Market_Price" in apple_df.columns:
            metrics['avg_price'] = apple_df["Market_Price"].mean()
        else:
            metrics['avg_price'] = 0
    
    return metrics

def create_combined_report(summaries):
    """
    Create a combined report from all summaries
    
    Args:
        summaries (dict): Dictionary containing summary data
        
    Returns:
        str: Combined report text
    """
    combined_report = "APPLE MARKET ANALYSIS REPORT\n"
    combined_report += "=" * 50 + "\n\n"
    
    for key, summary in summaries.items():
        combined_report += f"\n{'='*50}\n{key.upper().replace('_', ' ')} ANALYSIS\n{'='*50}\n\n{summary}\n\n"
    
    return combined_report
