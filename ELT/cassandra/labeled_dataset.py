import pandas as pd
from cassandra.cluster import Cluster
import datetime

# Read the CSV file into a DataFrame
df = pd.read_csv("./data/labeled_dataset.csv")

# Connect to the Cassandra cluster
cluster = Cluster(["localhost"])
session = cluster.connect("test")

# Prepare the insert query
insert_query = """
INSERT INTO labeled (timestamp, attention, meditation, delta, theta, lowalpha, highalpha, lowbeta, highbeta, lowgamma, middlegamma, classification)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""
prepared = session.prepare(insert_query)

# Insert data into Cassandra
for _, row in df.iterrows():
    row_data = [datetime.datetime.now()] + list(row) 

    session.execute(prepared, tuple(row_data))

# Close the connection
cluster.shutdown()
