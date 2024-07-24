import pandas as pd

df = pd.read_csv("data/acquiredDataset.csv")


# Step 1: Drop the 'attention' and 'meditation' columns
df = df.drop(columns=["attention", "meditation"])

# Step 2: Rename columns to use underscore format
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace("alpha", "_alpha")
df.columns = df.columns.str.replace("beta", "_beta")
df.columns = df.columns.str.replace("gamma", "_gamma")

# Display the modified DataFrame
df.to_csv("data/dataset3.csv", index=False)
