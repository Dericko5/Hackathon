# --------------------------------------------
# MachineLearning.py
# Description: Clusters missing kids data using KMeans
# --------------------------------------------

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# STEP 1: Load the CSV properly
#  - skiprows=1 : skip the first header row (",line,__fileposition__")
#  - usecols=[1] : only read column index 1 (the string with city,state,age,dateMissing)
#  - names=["location"] : name that column "location" temporarily
df = pd.read_csv(
    "Code/kids_features.csv",
    skiprows=1,
    usecols=[1],
    names=["location"],
    quotechar='"'
)

# STEP 2: Split the single "location" column into 4 separate columns
df[["city","state","age","dateMissing"]] = df["location"].str.split(",", expand=True)
df.drop(columns=["location"], inplace=True)

print("✅ Loaded data (first 5 rows):")
print(df.head())

# Convert age/dateMissing to numeric (if needed)
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["dateMissing"] = pd.to_numeric(df["dateMissing"], errors="coerce")

# STEP 3: Convert 'city' and 'state' from text to numeric codes for clustering
df["state_code"] = df["state"].astype("category").cat.codes
df["city_code"] = df["city"].astype("category").cat.codes

# STEP 4: Select features we want to cluster
features = df[["age", "state_code", "city_code"]]

# STEP 5: Scale the features (KMeans works better with scaled values)
scaler = StandardScaler()
scaled = scaler.fit_transform(features)

# STEP 6: Run KMeans clustering
kmeans = KMeans(n_clusters=3, random_state=42)
df["cluster"] = kmeans.fit_predict(scaled)

# STEP 7: Show a sample of the results
print("\nClustered data (first 5):")
print(df[["city", "state", "age", "cluster"]].head())

# STEP 8: Save the result to a CSV
df.to_csv("clustered_output.csv", index=False)
print("\n✅ Saved clustered data to 'clustered_output.csv'")

# STEP 9: (Optional) Visualize clusters
plt.figure(figsize=(10,6))
plt.scatter(df["age"], df["state_code"], c=df["cluster"], cmap="viridis")
plt.xlabel("Age")
plt.ylabel("State Code")
plt.title("Clustering of Missing Kids (Age vs State)")
plt.grid(True)
plt.savefig("clustering.png")
plt.show()
print("✅ Saved and displayed clustering graph.")
