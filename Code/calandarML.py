import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # ensures no interactive window is launched
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import calendar
import os

def parse_date_missing(x):
    """
    Convert integer-like 20250301 => Python datetime (YYYYMMDD).
    If fails, return None.
    """
    try:
        x_str = str(int(x)).zfill(8)
        return datetime.strptime(x_str, "%Y%m%d")
    except:
        return None

def main():
    # 1) Read your MISSINGKIDS.csv
    df = pd.read_csv("Code/MISSINGKIDS.csv", index_col=0)

    # Clean city/state if needed
    df["city"] = df["city"].str.strip().str.upper()
    df["state"] = df["state"].str.strip().str.upper()

    # Parse date
    df["date_parsed"] = df["datemissing"].apply(parse_date_missing)
    df = df.dropna(subset=["date_parsed"])

    # 2) Group by date -> missing_count
    group_data = df.groupby("date_parsed").size().reset_index(name="missing_count")

    # 3) Build a daily range from min_date to max_date
    min_date = group_data["date_parsed"].min()
    max_date = group_data["date_parsed"].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq="D")

    cal_df = pd.DataFrame({"date": all_dates})
    cal_df = cal_df.merge(group_data, left_on="date", right_on="date_parsed", how="left")
    cal_df.drop(columns=["date_parsed"], inplace=True)
    cal_df["missing_count"] = cal_df["missing_count"].fillna(0)

    # 4) day_of_week + week_index
    cal_df["day_of_week"] = cal_df["date"].dt.weekday  # Mon=0..Sun=6
    # find earliest Monday (or whatever start of week you prefer)
    earliest_monday = min_date - timedelta(days=min_date.weekday())
    # each column => # of weeks since earliest_monday
    cal_df["week_index"] = (cal_df["date"] - earliest_monday).dt.days // 7

    # 5) Pivot => rows=day_of_week(0..6), cols=week_index, values=missing_count
    pivot_df = cal_df.pivot(index="day_of_week", columns="week_index", values="missing_count")
    pivot_df = pivot_df.reindex(index=range(7), fill_value=0)

    # 6) Dynamically clamp figure width
    num_weeks = pivot_df.shape[1]
    # We use about 0.25 inch per column. Cap at e.g. 60 inches wide to avoid huge images
    width = min(num_weeks * 0.25, 60)
    height = 6  # can adjust as you like

    fig, ax = plt.subplots(figsize=(width, height))

    # Plot heatmap
    sns.heatmap(pivot_df, ax=ax, cmap="Greens", cbar=True,
                xticklabels=False, yticklabels=False)

    # 7) Add month labels
    ax.set_xlabel("")
    ax.set_ylabel("")
    # We'll label the first Monday of each month if it appears
    current_month = None
    for col in pivot_df.columns:
        monday_date = earliest_monday + timedelta(days=col*7)
        if monday_date.day == 1:
            month_name = calendar.month_abbr[monday_date.month]
            ax.text(col+0.5, -0.5, month_name, ha="center", va="center", rotation=0, fontsize=8)

    # day-of-week labels on the left
    dow_labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    for row_i, label in enumerate(dow_labels):
        ax.text(-0.5, row_i+0.5, label, ha="right", va="center", fontsize=8)

    # Invert y-axis so Mon=0 is at top
    ax.invert_yaxis()

    plt.title("GitHub-Style Heatmap: Missing Kids Per Day", fontsize=12)

    plt.tight_layout()
    outname = "github_style_heatmap_clamped.png"
    plt.savefig(outname, dpi=150)
    plt.close(fig)

    print(f"✅ Created {outname}.  (width={width:.1f} in, #weeks={num_weeks})")

if __name__ == "__main__":
    main()
