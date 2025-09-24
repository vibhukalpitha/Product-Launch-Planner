import os
import pandas as pd
import matplotlib.pyplot as plt
from ollama import chat
from prophet import Prophet
import matplotlib.lines as mlines

# --- Load data ---
df = pd.read_csv("Walmart_customer_fixed.csv", low_memory=False)
df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'], errors='coerce')

# --- Filter Apple sales ---
mask_brand = df['Brand'].fillna('').str.contains('apple', case=False, na=False)
mask_product = df['Product_Name'].fillna('').str.contains('apple', case=False, na=False)
apple_sales = df[mask_brand | mask_product].copy()

# --- Aggregate monthly revenue by product ---
monthly = (
    apple_sales
    .groupby([pd.Grouper(key="Purchase_Date", freq="ME"), "Product_Name"])["Purchase_Amount"]
    .sum()
    .reset_index()
)

# --- Pick top 5 products by total revenue ---
top_products = (
    monthly.groupby("Product_Name")["Purchase_Amount"]
    .sum()
    .nlargest(5)
    .index
)

monthly_top = monthly[monthly["Product_Name"].isin(top_products)]

# --- Ensure output folder ---
output_dir = "product_domination"
os.makedirs(output_dir, exist_ok=True)

summary_file = os.path.join(output_dir, "product_domination_summary.txt")
plot_file = os.path.join(output_dir, "product_domination_forecast.png")

# --- Forecast next 6 months for each product ---
plt.figure(figsize=(12, 6))
forecast_data = {}
colors = plt.cm.tab10.colors  # consistent colors for products

# Global last actual date (for divider line + shading)
global_last_date = monthly_top['Purchase_Date'].max()

for i, product in enumerate(top_products):
    product_data = (
        monthly_top[monthly_top['Product_Name'] == product]
        [['Purchase_Date', 'Purchase_Amount']]
        .rename(columns={'Purchase_Date': 'ds', 'Purchase_Amount': 'y'})
    )

    # Train Prophet
    model = Prophet()
    model.fit(product_data)

    # Make future dataframe
    future = model.make_future_dataframe(periods=6, freq='ME')
    forecast = model.predict(future)

    # Last actual date for THIS product
    last_actual_date = product_data['ds'].max()

    # Save forecast results (include last actual so line connects seamlessly)
    future_forecast = forecast[forecast['ds'] >= last_actual_date]
    forecast_data[product] = future_forecast[['ds', 'yhat']]

    # Plot actual history
    plt.plot(product_data['ds'], product_data['y'], marker='o', color=colors[i], label=product)

    # Plot forecast (continuous line, no gap)
    plt.plot(future_forecast['ds'], future_forecast['yhat'], linestyle="--", color=colors[i])

# --- Add divider line and shading (global cutoff) ---
plt.axvline(x=global_last_date, color="black", linestyle="--", linewidth=1.2)
plt.axvspan(global_last_date, forecast['ds'].max(), color="gray", alpha=0.15)

# --- Legend: Actual vs Forecast + Product colors ---
actual_line = mlines.Line2D([], [], color="black", linestyle="-", marker="o", label="Actual")
forecast_line = mlines.Line2D([], [], color="black", linestyle="--", label="Forecast")
product_lines = [mlines.Line2D([], [], color=colors[i], label=prod) for i, prod in enumerate(top_products)]

plt.legend(handles=[actual_line, forecast_line] + product_lines,
           bbox_to_anchor=(1.05, 1), loc="upper left")

# --- Final formatting ---
plt.title("Apple Top 5 Products: Sales Forecast (Next 6 Months)")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

# Save plot (instead of showing)
plt.savefig(plot_file, dpi=300, bbox_inches="tight")
plt.close()

# --- Prepare summary text for Ollama ---
last_data = monthly_top.groupby("Product_Name").tail(12)
series_text = "\n".join(f"{row.Purchase_Date:%Y-%m} | {row.Product_Name}: {row.Purchase_Amount:.2f}" for _, row in last_data.iterrows())

forecast_text = ""
for product, fcast in forecast_data.items():
    forecast_text += f"\n{product}:\n" + fcast.to_string(index=False)

prompt = f"""
Here is Apple monthly revenue for the top 5 products (last 12 months):
{series_text}

And here is the forecast for the next 6 months:
{forecast_text}

Please:
1. Summarize the past sales trends of these products.
2. Compare their forecast directions (growth/decline/stability).
3. Suggest possible business actions Apple could take for product strategy.
"""

print("⏳ Sending data to Gemma3, please wait...")

# --- Call Gemma3 ---
try:
    response = chat(model="gemma3", messages=[{"role": "user", "content": prompt}])

    # Save summary ONLY to file (not printing in terminal)
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(response['message']['content'])

    print("✅ Gemma3 has finished processing!")
    print(f"📊 Summary saved to: {summary_file}")
    print(f"📈 Plot saved to: {plot_file}")

except Exception as e:
    print("❌ Error while generating summary. Make sure Gemma3 is running and accessible.\n", e)
