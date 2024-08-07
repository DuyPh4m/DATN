#!/bin/bash

# Set Cassandra host and port
CASSANDRA_HOST=localhost
CASSANDRA_PORT=9042

# Set keyspace and table name
KEYSPACE=test
CLASSIFICATION_TABLE=classify
LABELED_TABLE=labeled
ACCURACY_TABLE=metrics

# Create keyspace
echo "CREATE KEYSPACE IF NOT EXISTS $KEYSPACE WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT

# Use keyspace
echo "USE $KEYSPACE;" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT

# Create prediction table
echo "CREATE TABLE IF NOT EXISTS $KEYSPACE.$CLASSIFICATION_TABLE ( timestamp timestamp, model_name text, user_id text, predicted_label int, PRIMARY KEY (user_id, timestamp));" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT

# Create labeled table
echo "CREATE TABLE IF NOT EXISTS $KEYSPACE.$LABELED_TABLE ( timestamp timestamp PRIMARY KEY, delta int, theta int, low_alpha int, high_alpha int, low_beta int, high_beta int, low_gamma int, middle_gamma int, classification int);" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT

# Create accuracy table
echo "CREATE TABLE IF NOT EXISTS $KEYSPACE.$ACCURACY_TABLE ( timestamp timestamp, user_id text, model_name text, weighted_recall float, f1_score float, accuracy float, duration text, PRIMARY KEY (user_id, timestamp));" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT


if [ $? -eq 0 ]
then
  echo "Cassandra setup successfully."
else
  echo "Cassandra setup failed."
  exit 1
fi