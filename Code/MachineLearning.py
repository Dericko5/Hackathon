# --------------------------------------------
# machine_learning.py
# Description:
# 1) Loads MISSINGKIDS.csv, merges w/ hospitals/fire/police, merges lat/lng from HMKuscities.csv
# 2) Groups + clusters (KMeans)
# 3) Outputs final "merged_missingkids_infra.csv" w/ lat/lng + numeric columns
# --------------------------------------------

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    # ===== 1) LOAD & GROUP MISSINGKIDS =====
    df_kids = pd.read_csv("Code/MISSINGKIDS.csv", index_col=0)
    # Group by city/state => missing_kids + avg_age + avg_risk
    df_kids_counts = df_kids.groupby(["city","state"]).size().reset_index(name="missing_kids")
    kids_extra = df_kids.groupby(["city","state"]).agg({"age":"mean","riskscore":"mean"}).reset_index()
    kids_extra.rename(columns={"age":"avg_age","riskscore":"avg_risk"}, inplace=True)
    df_kids_merged = df_kids_counts.merge(kids_extra, on=["city","state"], how="left")

    # ===== 2) LOAD & GROUP HOSPITALS, FIRE, POLICE =====
    df_hosp = pd.read_csv("Code/HMKHospitals.csv")
    df_fire = pd.read_csv("Code/HMKFire_Stations.csv")
    df_police = pd.read_csv("Code/HMKPolice.csv")

    # Rename and group
    df_hosp.rename(columns={"CITY":"city","STATE":"state"}, inplace=True)
    df_fire.rename(columns={"CITY":"city","STATE":"state"}, inplace=True)
    df_police.rename(columns={"CITY":"city","STATE":"state"}, inplace=True)

    df_hosp_counts = df_hosp.groupby(["city","state"]).size().reset_index(name="num_hospitals")
    df_fire_counts = df_fire.groupby(["city","state"]).size().reset_index(name="num_firestations")
    df_police_counts = df_police.groupby(["city","state"]).size().reset_index(name="num_police")

    merged_df = df_kids_merged.merge(df_hosp_counts, on=["city","state"], how="left")
    merged_df = merged_df.merge(df_fire_counts, on=["city","state"], how="left")
    merged_df = merged_df.merge(df_police_counts, on=["city","state"], how="left")

    for col in ["num_hospitals","num_firestations","num_police"]:
        merged_df[col] = merged_df[col].fillna(0)

    # ===== 3) MERGE LAT/LNG FROM HMKuscities =====
    df_cities = pd.read_csv("Code/HMKuscities.csv")
    # Avoid duplicates
    if "city" in df_cities.columns:
        df_cities.rename(columns={"city":"city_orig"}, inplace=True)
    df_cities.rename(columns={"city_ascii":"city","state_id":"state"}, inplace=True)

    merged_df = merged_df.merge(df_cities[["city","state","lat","lng"]], on=["city","state"], how="left")

    # ===== 4) KMEANS CLUSTERING =====
    feature_cols = ["avg_age","avg_risk","missing_kids","num_hospitals","num_firestations","num_police"]
    for col in feature_cols:
        merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce").fillna(0)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(merged_df[feature_cols])

    kmeans = KMeans(n_clusters=3, random_state=42)
    merged_df["cluster"] = kmeans.fit_predict(scaled)

    # Save final DataFrame
    merged_df.to_csv("merged_missingkids_infra.csv", index=False)
    print("✅ Clustering complete. Data saved to 'merged_missingkids_infra.csv'")

    # Optional quick plot
    state_group = merged_df.groupby("state")["missing_kids"].sum().reset_index()

    plt.figure(figsize=(12, 6))
    sns.barplot(data=state_group, x="state", y="missing_kids", palette="mako")
    plt.title("Total Missing Kids by State")
    plt.xlabel("State")
    plt.ylabel("Missing Children Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("better_plot.png")
    plt.show()

if __name__ == "__main__":
    main()
