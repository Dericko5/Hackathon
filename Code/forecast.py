import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from datetime import datetime, timedelta
import itertools

def parse_date_missing(x):
    """
    Convert integer-like 20250301 => Python datetime (YYYYMMDD).
    Return None if parsing fails.
    """
    try:
        x_str = str(int(x)).zfill(8)
        return datetime.strptime(x_str, "%Y%m%d")
    except:
        return None

def generate_holiday_df(start_year=2019, end_year=2026):
    """
    Build a list of holiday events for each year between start_year and end_year.
    We'll add Valentines, July4, Halloween, Christmas, NewYears, etc.
    Optionally define +/- windows if you suspect the holiday effect extends days around it.
    """
    # For each year in that range, we define certain fixed holidays.
    # If you want more, just add them below.
    holiday_rows = []
    
    # We define the holiday names + month/day
    holiday_definitions = [
        ("NewYears", 1, 1),
        ("Valentines", 2, 14),
        ("July4", 7, 4),
        ("Halloween", 10, 31),
        ("Christmas", 12, 25),
    ]
    
    for year in range(start_year, end_year + 1):
        for (name, m, d) in holiday_definitions:
            try:
                dt = datetime(year, m, d)
                holiday_rows.append({"holiday": name, "ds": dt})
            except ValueError:
                # if something invalid (e.g. doesn't exist), skip
                pass
    
    # Convert to DataFrame
    holiday_df = pd.DataFrame(holiday_rows)
    
    # Optionally define windows around each holiday
    # For example, +- 1 day:
    # holiday_df["lower_window"] = 0
    # holiday_df["upper_window"] = 1
    return holiday_df


def main():
    # ----- 1) Load MISSINGKIDS.csv -----
    df = pd.read_csv("Code/MISSINGKIDS.csv", index_col=0)
    # columns = [ city, state, age, datemissing, firstname, lastname, etc. ]
    
    # Clean city/state if needed
    df["city"] = df["city"].str.strip().str.upper()
    df["state"] = df["state"].str.strip().str.upper()
    
    # Parse date
    df["date_parsed"] = df["datemissing"].apply(parse_date_missing)
    df = df.dropna(subset=["date_parsed"])
    
    # ----- 2) Filter for recent years only (2019 onward) -----
    df = df[df["date_parsed"] >= datetime(2019,1,1)]
    # If you want e.g. 2020 onward, adjust above line
    
    # ----- 3) Aggregate daily missing kids -----
    daily_counts = df.groupby("date_parsed").size().reset_index(name="missing_count")
    
    # For Prophet, rename columns to ds (date) and y (value)
    daily_counts.rename(columns={"date_parsed":"ds", "missing_count":"y"}, inplace=True)
    # Sort by ds
    daily_counts = daily_counts.sort_values("ds")

    if len(daily_counts) < 10:
        print("⚠ Not enough recent data after 2019 to model. Exiting...")
        return
    
    # ----- 4) Build a holiday DataFrame for 2019..2026 (adjust if needed) -----
    holiday_df = generate_holiday_df(start_year=2019, end_year=2026)
    
    # ----- 5) Create the Prophet model, with holiday info -----
    model = Prophet(
        weekly_seasonality=True,
        yearly_seasonality=True,
        holidays=holiday_df
    )
    
    # ----- 6) Fit the model on daily_counts -----
    model.fit(daily_counts)
    
    # ----- 7) Create future periods (e.g. 180 days after last date) -----
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)
    
    # ----- 8) Plot the forecast -----
    fig1 = model.plot(forecast)
    ax1 = fig1.axes[0] 
    ax1.set_title("Missing Kids Forecast (with Holiday Effects)", fontsize=14)
    ax1.set_xlabel("Date", fontsize=12)
    ax1.set_ylabel("Number of Missing Children Daily", fontsize=12)
    fig1.savefig("forecast_recent.png", dpi=150)
    
    # Components: weekly, yearly, holidays
    fig2 = model.plot_components(forecast)
    fig2.suptitle("Prophet Components: Weekly, Yearly, and Holiday Effects", fontsize=14)
    fig2.savefig("forecast_components.png", dpi=150)
    
    print("✅ Forecast plots saved: 'forecast_recent.png' and 'forecast_components.png'.")

if __name__ == "__main__":
    main()
