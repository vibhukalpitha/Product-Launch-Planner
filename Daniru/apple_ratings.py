import os
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet

print("⏳ Loading dataset...")
df = pd.read_csv("Walmart_customer_fixed.csv", low_memory=False)
df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'], errors='coerce')

print("⏳ Filtering Apple-related sales...")
mask_brand = df['Brand'].fillna('').str.contains('apple', case=False, na=False)
mask_product = df['Product_Name'].fillna('').str.contains('apple', case=False, na=False)
apple_sales = df[mask_brand | mask_product].copy()

# --- Ensure Ratings column exists ---
if 'Rating' not in apple_sales.columns:
    raise ValueError("❌ The dataset does not contain a 'Rating' column.")

print("⏳ Aggregating monthly average ratings...")
monthly_rating = (
    apple_sales
    .set_index('Purchase_Date')
    .resample('ME')['Rating']
    .mean()
    .reset_index()
)

# --- Prepare data for Prophet ---
rating_df = monthly_rating.rename(columns={'Purchase_Date': 'ds', 'Rating': 'y'})

print("⏳ Training Prophet model...")
model = Prophet()
model.fit(rating_df)

print("⏳ Forecasting next 6 months...")
future = model.make_future_dataframe(periods=6, freq='ME')
forecast = model.predict(future)

# --- Ensure output folder ---
output_dir = "apple_ratings"
os.makedirs(output_dir, exist_ok=True)

summary_file = os.path.join(output_dir, "apple_ratings_summary.txt")
plot_file = os.path.join(output_dir, "apple_ratings_forecast.png")

print("⏳ Generating plot...")
plt.figure(figsize=(10, 5))

# Actual ratings
plt.plot(rating_df['ds'], rating_df['y'], marker='o', color="purple", label="Actual Avg Rating")

# Forecast ratings
last_actual_date = rating_df['ds'].max()
forecast_part = forecast[forecast['ds'] >= last_actual_date]
plt.plot(forecast_part['ds'], forecast_part['yhat'], linestyle="--", color="orange", label="Forecast Avg Rating")

# Divider line & shading
plt.axvline(x=last_actual_date, color="black", linestyle="--", linewidth=1.2)
plt.axvspan(last_actual_date, forecast['ds'].max(), color="gray", alpha=0.15)

# Formatting
plt.title("Apple Average Rating Forecast (Next 6 Months)")
plt.xlabel("Month")
plt.ylabel("Average Rating")
plt.ylim(0, 5)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()

# Save plot
plt.savefig(plot_file, dpi=300, bbox_inches="tight")
plt.close()
print(f"📈 Plot saved to: {plot_file}")

print("⏳ Writing summary file...")
last_text = "\n".join(f"{row.ds:%Y-%m}: {row.y:.2f}" for _, row in rating_df.tail(12).iterrows())
future_text = "\n".join(f"{row.ds:%Y-%m}: {row.yhat:.2f}" for _, row in forecast_part.tail(6).iterrows())

summary_text = f"""
📊 Apple Ratings Forecast Summary

Total months analyzed: {len(rating_df)}
Average rating overall: {rating_df['y'].mean():.2f}

Last 12 months of ratings:
{last_text}

Next 6 months (forecasted ratings):
{future_text}
"""

with open(summary_file, "w", encoding="utf-8") as f:
    f.write(summary_text)

print(f"📊 Summary saved to: {summary_file}")
print("✅ Processing finished!")
