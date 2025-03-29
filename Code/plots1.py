import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create output directory for graphs
output_dir = "graphs"
os.makedirs(output_dir, exist_ok=True)

# ----------------------------- #
# 1. MISSINGKIDS.csv – State-Level Metrics
# ----------------------------- #
# Expected format for MISSINGKIDS.csv:
# index, city, state, age, datemissing, firstname, lastname, riskscore, cluster
df_kids = pd.read_csv("Code/MISSINGKIDS.csv", index_col=0)

# Clean city/state strings (trim and uppercase)
df_kids["state"] = df_kids["state"].str.strip().str.upper()
df_kids["city"] = df_kids["city"].str.strip().str.upper()

# Group by state: count missing kids, average age, average risk score
kids_by_state = df_kids.groupby("state").agg(
    missing_kids_count=("state", "count"),
    avg_age=("age", "mean"),
    avg_risk=("riskscore", "mean")
).reset_index()

# ----------------------------- #
# 2. teenpregnancy.csv – State-Level Data
# ----------------------------- #
# Format: YEAR, STATE, RATE, URL
df_teen = pd.read_csv("Code/teenpregnancy.csv")
# Clean and filter for 2021
df_teen["STATE"] = df_teen["STATE"].str.strip().str.upper()
df_teen_2021 = df_teen[df_teen["YEAR"] == 2021].copy()
df_teen_2021.rename(columns={"STATE": "state", "RATE": "teen_preg_rate"}, inplace=True)
# We assume one row per state; if there are duplicates, group by state (here we take mean)
df_teen_2021 = df_teen_2021.groupby("state").agg({"teen_preg_rate": "mean"}).reset_index()

# ----------------------------- #
# 3. state-divorce-rates-90-95-99-21.csv – State-Level Data
# ----------------------------- #
# Format: State, Y2021, Y2020, ...
df_divorce = pd.read_csv("Code/state-divorce-rates-90-95-99-21.csv")
df_divorce["State"] = df_divorce["State"].str.strip().str.upper()
df_divorce.rename(columns={"State": "state", "Y2021": "divorce_rate_2021"}, inplace=True)
# If there are extra columns, keep only state and divorce_rate_2021:
df_divorce = df_divorce[["state", "divorce_rate_2021"]]

# ----------------------------- #
# 4. airports.csv – State-Level Data
# ----------------------------- #
# Format: State/Territory,Number of Airports
df_air = pd.read_csv("Code/airports.csv")
df_air.rename(columns={"State/Territory": "state", "Number of Airports": "num_airports"}, inplace=True)
# Clean state names:
df_air["state"] = df_air["state"].str.strip().str.upper()
# If necessary, group by state (if multiple rows exist):
df_air = df_air.groupby("state").agg({"num_airports": "sum"}).reset_index()

# ----------------------------- #
# 5. Merge the Datasets on 'state'
# ----------------------------- #
# We'll merge our base (kids_by_state) with teen pregnancy, divorce, and airports.
merged_state = kids_by_state.merge(df_teen_2021, on="state", how="left")
merged_state = merged_state.merge(df_divorce, on="state", how="left")
merged_state = merged_state.merge(df_air, on="state", how="left")

# Fill missing values with 0
merged_state.fillna(0, inplace=True)
print("Merged State-Level Data:")
print(merged_state.head())

# ----------------------------- #
# 6. Compute Correlation Matrix
# ----------------------------- #
cols_for_corr = ["missing_kids_count", "avg_age", "avg_risk", "teen_preg_rate", "divorce_rate_2021", "num_airports"]
corr_matrix = merged_state[cols_for_corr].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Matrix (State-Level)")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "correlation_matrix.png"))
plt.close()

# ----------------------------- #
# 7. Scatter Plot: Teen Pregnancy vs Missing Kids Count
# ----------------------------- #
plt.figure(figsize=(10, 6))
sns.scatterplot(data=merged_state, x="teen_preg_rate", y="missing_kids_count", s=100, color="purple")
plt.title("Teen Pregnancy Rate vs Missing Kids Count (by State)")
plt.xlabel("Teen Pregnancy Rate (per 1,000)")
plt.ylabel("Missing Kids Count")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "teenpreg_vs_missingkids.png"))
plt.close()

# ----------------------------- #
# 8. Bar Chart: Average Age of Missing Kids by State
# ----------------------------- #
state_avg_age = df_kids.groupby("state")["age"].mean().sort_values(ascending=False)
plt.figure(figsize=(12, 6))
state_avg_age.plot(kind="bar", color="skyblue")
plt.title("Average Age of Missing Kids by State")
plt.xlabel("State")
plt.ylabel("Average Age")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "avg_age_by_state.png"))
plt.close()

print("✅ Graphs generated and saved in the 'graphs/' folder.")
