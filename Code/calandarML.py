import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from datetime import datetime

def parse_date_missing(x):
    """ Parse YYYYMMDD integer/string into Python datetime. """
    try:
        x_str = str(int(x)).zfill(8)
        return datetime.strptime(x_str, "%Y%m%d")
    except:
        return None

def main():
    # 1) Load MISSINGKIDS.csv
    df = pd.read_csv("Code/MISSINGKIDS.csv", index_col=0)
    # columns: [city, state, age, datemissing, firstname, lastname, riskscore, cluster]
    
    # 2) Parse date
    df["date_parsed"] = df["datemissing"].apply(parse_date_missing)
    # Drop rows with invalid date
    df = df.dropna(subset=["date_parsed"])
    
    # 3) Aggregate daily missing kids count
    daily_counts = df.groupby("date_parsed").size().reset_index(name="missing_count")
    # Rename columns to 'ds' and 'y' for Prophet
    # ds = date, y = value to forecast
    daily_counts.rename(columns={"date_parsed":"ds", "missing_count":"y"}, inplace=True)
    daily_counts = daily_counts.sort_values("ds")
    
    # 4) Build a holiday dataframe for major holidays
    # We'll assume the data spans e.g. 2024..2026 or so. 
    # Adjust date ranges/years as needed.
    # We'll guess a few holiday DS. Expand if you have multiple years.
    holiday_list = [
        # name, date
        ("Valentines", "2025-02-14"),
        ("Valentines", "2026-02-14"),
        ("Halloween",  "2025-10-31"),
        ("Halloween",  "2026-10-31"),
        ("Christmas",  "2025-12-25"),
        ("Christmas",  "2026-12-25"),
    ]
    # Turn that list into a DataFrame
    holiday_df = pd.DataFrame({
        "holiday": [h[0] for h in holiday_list],
        "ds": [pd.to_datetime(h[1]) for h in holiday_list],
    })
    # If you want a ± window around each holiday, add 'lower_window' / 'upper_window'
    # holiday_df["lower_window"] = 0
    # holiday_df["upper_window"] = 1  # etc.
    
    # 5) Initialize Prophet with holidays
    model = Prophet(
        weekly_seasonality=True,
        yearly_seasonality=True,
        holidays=holiday_df
    )
    
    # 6) Fit the model
    model.fit(daily_counts)
    
    # 7) Make a future dataframe for predictions
    # Let's predict 60 days after the last date
    future = model.make_future_dataframe(periods=60)
    forecast = model.predict(future)
    
    # 8) Plot the forecast
    fig1 = model.plot(forecast)
    fig1.savefig("forecast_plot.png", dpi=150)
    
    # 9) Plot holiday/seasonality components
    fig2 = model.plot_components(forecast)
    fig2.savefig("forecast_components.png", dpi=150)
    
    print("✅ Forecast saved. Check 'forecast_plot.png' & 'forecast_components.png'")

if __name__ == "__main__":
    main()
