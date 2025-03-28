# --------------------------------------------
# MachineLearning.py
# Description: Merges multiple normal CSVs on (city, state), then runs KMeans.
# --------------------------------------------

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def main():
    """
    1) Load multiple CSVs that share 'city', 'state'.
    2) Merge them all.
    3) Pick numeric columns for KMeans.
    4) Run KMeans + save results.
    """
    # ----- A) LOAD DATASETS -----
    # Example: HMKEducation.csv, HMKPoverty.csv, HMKPopulation.csv
    df_edu = pd.read_csv("Code/HMKEducation.csv")
    df_pov = pd.read_csv("Code/HMKPoverty.csv")
    df_pop = pd.read_csv("Code/HMKPopulation.csv")
    
    # Optionally load more CSVs if needed:
    # df_crime = pd.read_csv("Code/HMKCrime.csv")
    # df_unemp = pd.read_csv("Code/HMKUnemployment.csv")
    
    # ----- B) MERGE THEM SEQUENTIALLY -----
    # Start with one, merge the others on (city, state).
    # Adjust the how="left"/"inner" depending on your preference.
    merged_df = df_edu.merge(df_pov, on=["city","state"], how="left")
    merged_df = merged_df.merge(df_pop, on=["city","state"], how="left")
    
    # If you have more, keep merging:
    # merged_df = merged_df.merge(df_crime, on=["city","state"], how="left")
    # merged_df = merged_df.merge(df_unemp, on=["city","state"], how="left")
    
    print("✅ Merged DataFrame shape:", merged_df.shape)
    print("Columns:", merged_df.columns.tolist())
    
    # ----- C) CHOOSE FEATURES (NUMERIC COLUMNS) -----
    # Suppose each CSV has numeric columns like 'education_level', 'poverty_rate', 'population'.
    # Adjust these to match your real column names.
    feature_cols = ["education_level", "poverty_rate", "population"]
    # Add more if you have them, e.g.:
    # feature_cols += ["crime_rate", "unemployment_rate"]
    
    # Fill NaN for numeric columns (quick hack for missing data)
    merged_df[feature_cols] = merged_df[feature_cols].fillna(0)
    
    # Check data types, convert if needed:
    # merged_df["education_level"] = pd.to_numeric(merged_df["education_level"], errors="coerce")
    # merged_df["poverty_rate"] = pd.to_numeric(merged_df["poverty_rate"], errors="coerce")
    # ...
    
    # ----- D) SCALE FEATURES -----
    features = merged_df[feature_cols]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    
    # ----- E) KMEANS -----
    kmeans = KMeans(n_clusters=3, random_state=42)
    merged_df["cluster"] = kmeans.fit_predict(scaled)
    
    # ----- F) SAVE / PREVIEW RESULTS -----
    merged_df.to_csv("multi_dataset_clustered.csv", index=False)
    print("\n✅ Clustering complete. Results saved to 'multi_dataset_clustered.csv'")
    
    # Optional: simple scatter plot using any 2 numeric columns
    plt.figure(figsize=(8,5))
    plt.scatter(merged_df["education_level"], merged_df["poverty_rate"], c=merged_df["cluster"], cmap="viridis")
    plt.xlabel("Education Level")
    plt.ylabel("Poverty Rate")
    plt.title("Multi-CSV KMeans Clustering")
    plt.grid(True)
    plt.savefig("multi_dataset_clustering.png")
    plt.show()
    print("✅ Scatter plot saved to 'multi_dataset_clustering.png'")

if __name__ == "__main__":
    main()
