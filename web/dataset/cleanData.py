import pandas as pd

df = pd.read_csv('web/dataset/acquiredDataset.csv', index_col=False)

# print(df.drop(columns='classification'))

df.drop(columns='classification').to_csv('web/dataset/cleanedDataset.csv', index=False)