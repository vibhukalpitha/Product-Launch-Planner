import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from ollama import chat
import os

# --- Create results folder ---
output_dir = "price_elasticity"
os.makedirs(output_dir, exist_ok=True)

# --- Load data ---
df = pd.read_csv("Walmart_customer_fixed.csv", low_memory=False)
df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'], errors='coerce')

# --- Filter Apple sales ---
mask_brand = df['Brand'].fillna('').str.contains('apple', case=False, na=False)
mask_product = df['Product_Name'].fillna('').str.contains('apple', case=False, na=False)
apple_sales = df[mask_brand | mask_product].copy()

# --- Aggregate monthly sales and average price ---
monthly_sales = apple_sales.set_index('Purchase_Date').resample('ME').agg({
    'Purchase_Amount': 'sum',
    'Market_Price': 'mean'
}).reset_index()

monthly_sales.rename(columns={
    'Purchase_Amount': 'Sales',
    'Market_Price': 'AvgPrice'
}, inplace=True)

# --- Forecast Sales ---
sales_df = monthly_sales[['Purchase_Date','Sales']].rename(columns={'Purchase_Date':'ds','Sales':'y'})
model_sales = Prophet()
model_sales.fit(sales_df)
future_sales = model_sales.make_future_dataframe(periods=6, freq='ME')
forecast_sales = model_sales.predict(future_sales)

# --- Forecast Price ---
price_df = monthly_sales[['Purchase_Date','AvgPrice']].rename(columns={'Purchase_Date':'ds','AvgPrice':'y'})
model_price = Prophet()
model_price.fit(price_df)
future_price = model_price.make_future_dataframe(periods=6, freq='ME')
forecast_price = model_price.predict(future_price)

# --- Merge forecasts ---
merged = forecast_sales[['ds','yhat']].rename(columns={'yhat':'Sales_Forecast'})
merged['Price_Forecast'] = forecast_price['yhat'].values

# --- Plot combined Sales + Price forecast ---
fig, ax1 = plt.subplots(figsize=(10,5))

ax1.set_xlabel("Date")
ax1.set_ylabel("Sales (blue)", color="blue")
ax1.plot(merged['ds'], merged['Sales_Forecast'], color="blue", label="Sales Forecast")
ax1.tick_params(axis='y', labelcolor="blue")

ax2 = ax1.twinx()
ax2.set_ylabel("Average Price (red)", color="red")
ax2.plot(merged['ds'], merged['Price_Forecast'], color="red", label="Price Forecast")
ax2.tick_params(axis='y', labelcolor="red")

# --- Add vertical line to separate history vs forecast ---
last_actual_date = monthly_sales['Purchase_Date'].max()
plt.axvline(x=last_actual_date, color="gray", linestyle="--", linewidth=1)
plt.text(last_actual_date, ax1.get_ylim()[1]*0.95, "Forecast starts →", 
         rotation=0, color="gray", ha="left", va="top")

plt.title("Apple Sales vs Price Forecast (Next 6 Months)")
plt.grid(True)

# --- Save plot into price_elasticity folder ---
plot_path = os.path.join(output_dir, "price_elasticity_forecast.png")
plt.savefig(plot_path)
plt.close()

# --- Prepare summary for Gemma3 ---
last_data = monthly_sales.tail(12)
last_text = "\n".join(f"{row.Purchase_Date:%Y-%m}: Price={row.AvgPrice:.2f}, Sales={row.Sales:.2f}"
                      for _, row in last_data.iterrows())

future_text = "\n".join(f"{row.ds:%Y-%m}: Price={row.Price_Forecast:.2f}, Sales={row.Sales_Forecast:.2f}" 
                        for _, row in merged.tail(6).iterrows())

prompt = f"""
Here are Apple monthly average prices and sales:

Last 12 months (actuals):
{last_text}

Next 6 months (forecast):
{future_text}

Please:
1. Summarize how sales have moved with price in the past.
2. Explain the forecast for the next 6 months (does sales fall if price rises, or vice versa?).
3. Suggest business actions Apple could take.
"""

print("⏳ Sending forecast data to Gemma3, please wait...")

try:
    response = chat(model="gemma3", messages=[{"role":"user","content":prompt}])
    summary_text = response['message']['content']

    # --- Save summary as text file ---
    summary_path = os.path.join(output_dir, "price_elasticity_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print("✅ Gemma3 has finished processing!")
    print(f"📊 Summary saved to: {summary_path}")
    print(f"📈 Plot saved to: {plot_path}")

except Exception as e:
    print("❌ Error while generating summary. Make sure Gemma3 is running and accessible.\n", e)
