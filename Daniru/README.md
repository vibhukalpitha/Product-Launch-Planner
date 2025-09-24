# 🍎 Apple Market Analyzer Dashboard

A comprehensive Streamlit dashboard for analyzing Apple's market performance, featuring analysis, predictions, and insights.

## 📊 Features

### 🏠 Overview Dashboard
- Key metrics and KPIs
- Market share visualization
- Apple ratings distribution
- Sales performance indicators

### 📈 Feature Analysis
- **Geographic Insights**: Top cities by Apple sales
- **Price Analysis**: Price vs sales relationship
- **Discount Impact**: Effect of discounts on sales
- **Time-based Trends**: Monthly and weekly sales patterns

### 🔮 Predictions
- **Ratings Forecast**: Future rating predictions
- **Sales Forecast**: Revenue projections
- **Price Elasticity**: Price sensitivity analysis
- **Product Domination**: Market dominance predictions

### 📊 Market Insights
- **Seasonal Analysis**: Holiday and back-to-school trends
- **Product Categories**: Performance by product type
- **Customer Demographics**: Age group analysis

### 📋 Reports
- Comprehensive analysis reports
- Downloadable combined reports
- Summary insights and recommendations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Required packages (see requirements.txt)

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the dashboard**:
   ```bash
   streamlit run app.py
   ```

3. **Access the dashboard**:
   - Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
Daniru/
├── app.py                          # Main Streamlit application
├── utils.py                        # Utility functions
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── F_A.ipynb                       # Feature analysis notebook
├── Walmart_customer_fixed.csv      # Main dataset
├── apple_ratings/                  # Ratings analysis
│   ├── apple_ratings_forecast.png
│   └── apple_ratings_summary.txt
├── apple_sales/                    # Sales analysis
│   ├── apple_sales_forecast.png
│   └── apple_sales_summary.txt
├── price_elasticity/               # Price elasticity analysis
│   ├── price_elasticity_forecast.png
│   └── price_elasticity_summary.txt
└── product_domination/             # Product domination analysis
    ├── product_domination_forecast.png
    └── product_domination_summary.txt
```

## 📊 Data Requirements

The dashboard expects the following data structure in `Walmart_customer_fixed.csv`:

### Required Columns:
- `Brand`: Product brand (filtered for "Apple")
- `Purchase_Date`: Date of purchase
- `Purchase_Amount`: Sales amount
- `Market_Price`: Product price
- `Rating`: Customer rating
- `City`: Customer location
- `Discount_Applied`: Whether discount was applied

### Optional Columns:
- `Product_Category`: Product type
- `Age_Group`: Customer age group

## 🎯 Key Insights

### Market Performance
- Apple's market share and positioning
- Customer satisfaction (ratings)
- Revenue trends and patterns

### Predictive Analytics
- Future sales forecasts
- Rating predictions
- Price elasticity analysis
- Product dominance trends

### Business Intelligence
- Geographic market opportunities
- Seasonal sales patterns
- Discount strategy effectiveness
- Customer demographic insights

## 🔧 Customization

### Adding New Analysis
1. Create new analysis functions in `utils.py`
2. Add corresponding sections in `app.py`
3. Update the navigation menu

### Styling
- Modify the CSS in the `st.markdown()` sections
- Update color schemes in plotly charts
- Customize layout and spacing

### Data Sources
- Update file paths in `utils.py` for different data sources
- Modify data cleaning logic for different data formats

## 📈 Usage Tips

1. **Navigation**: Use the sidebar to switch between different analysis sections
2. **Interactive Charts**: Hover over charts for detailed information
3. **Download Reports**: Use the Reports section to download comprehensive analysis
4. **Real-time Updates**: Refresh the page to see updated data

## 🛠️ Troubleshooting

### Common Issues:

1. **Data not loading**:
   - Ensure `Walmart_customer_fixed.csv` is in the correct location
   - Check file permissions and format

2. **Images not displaying**:
   - Verify forecast images are in the correct folders
   - Check image file formats (PNG recommended)

3. **Performance issues**:
   - Use `@st.cache_data` for data loading functions
   - Consider data sampling for large datasets

## 📞 Support

For issues or questions:
1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Ensure data files are in the expected locations

## 🔄 Updates

To update the dashboard:
1. Pull the latest changes
2. Install any new dependencies: `pip install -r requirements.txt`
3. Restart the Streamlit application

---

**🍎 Apple Market Analyzer Dashboard** - Powered by Streamlit
