import pandas as pd
from cassandra.cluster import Cluster
import datetime

# Read the CSV file into a DataFrame
df = pd.read_csv("./data/dataset3.csv")

# Connect to the Cassandra cluster
cluster = Cluster(["localhost"])
session = cluster.connect("test")

# Prepare the insert query
insert_query = """
INSERT INTO labeled (timestamp, delta, theta, low_alpha, high_alpha, low_beta, high_beta, low_gamma, middle_gamma, classification)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""
prepared_insert = session.prepare(insert_query)

# Prepare the select query to check for duplicates
select_query = """
SELECT * FROM labeled WHERE delta = ? AND theta = ? AND low_alpha = ? AND high_alpha = ? AND low_beta = ? AND high_beta = ? AND low_gamma = ? AND middle_gamma = ? ALLOW FILTERING;
"""
prepared_select = session.prepare(select_query)

# Iterate over the DataFrame rows
for _, row in df.iterrows():
    delta, theta, low_alpha, high_alpha, low_beta, high_beta, low_gamma, middle_gamma = (
        row["delta"],
        row["theta"],
        row["low_alpha"],
        row["high_alpha"],
        row["low_beta"],
        row["high_beta"],
        row["low_gamma"],
        row["middle_gamma"],
    )
    # Execute the select query
    results = session.execute(
        prepared_select, (delta, theta, low_alpha, high_alpha, low_beta, high_beta, low_gamma, middle_gamma)
    )
    # Check if the results are empty
    # if results.current_rows:
    #     print('Skipping duplicate row')
    #     continue  # Skip inserting duplicate values
    # else:
        # Prepare the row data for insertion
    row_data = [datetime.datetime.now()] + list(row)
    session.execute(prepared_insert, tuple(row_data))

# Close the connection
cluster.shutdown()
