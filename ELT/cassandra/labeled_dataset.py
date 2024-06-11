import pandas as pd
from cassandra.cluster import Cluster
import datetime

# Read the CSV file into a DataFrame
df = pd.read_csv("./data/labeled_dataset.csv")

# df = df.drop(columns=['attention', 'meditation', 'middlegamma', 'lowgamma'])

# Connect to the Cassandra cluster
cluster = Cluster(["localhost"])
session = cluster.connect("test")

# Prepare the insert query
insert_query = """
INSERT INTO labeled (timestamp, delta, theta, lowalpha, highalpha, lowbeta, highbeta, classification)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
"""
prepared = session.prepare(insert_query)

# Insert data into Cassandra
for _, row in df.iterrows():
    row_data = [datetime.datetime.now()] + list(row)

    session.execute(prepared, tuple(row_data))

# Close the connection
cluster.shutdown()
