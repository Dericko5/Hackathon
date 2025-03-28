import pandas as pd
df = pd.read_csv('Code/kids_features.csv', header=None, names=['city', 'state', 'age', 'dateMissing'])

print(df.head())
print(df.info())
print(df.describe())

df['state_code'] = df['state'].astype('category').cat.codes
df['city_code'] = df['city'].astype('category').cat.codes

from sklearn.cluster import KMeans

features = df[['age', 'state_code', 'city_code']]

kmeans = KMeans(n_clusters=3)
df['cluster'] = kmeans.fit_predict(features)

print(df[['city', 'state', 'age', 'cluster']].head())
