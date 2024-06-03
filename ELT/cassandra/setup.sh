#!/bin/bash

# Set Cassandra host and port
CASSANDRA_HOST=localhost
CASSANDRA_PORT=9042

# Set keyspace and table name
KEYSPACE=test
RAW_TABLE=raw
LABELED_TABLE=labeled
ACCURACY_TABLE=accuracy

# Create keyspace
echo "CREATE KEYSPACE IF NOT EXISTS $KEYSPACE WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT

# Use keyspace
echo "USE $KEYSPACE;" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT

# Create raw table
echo "CREATE TABLE IF NOT EXISTS $KEYSPACE.$RAW_TABLE ( timestamp timestamp PRIMARY KEY, attention int, meditation int, delta int, theta int, lowAlpha int, highAlpha int, lowBeta int, highBeta int, lowGamma int, middleGamma int);" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT

# Create labeled table
echo "CREATE TABLE IF NOT EXISTS $KEYSPACE.$LABELED_TABLE ( timestamp timestamp PRIMARY KEY, attention int, meditation int, delta int, theta int, lowAlpha int, highAlpha int, lowBeta int, highBeta int, lowGamma int, middleGamma int, classification int);" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT

# Create accuracy table
echo "CREATE TABLE IF NOT EXISTS $KEYSPACE.$ACCURACY_TABLE ( timestamp timestamp, user_id text, model text, accuracy float, duration text, PRIMARY KEY (user_id, timestamp));" | cqlsh $CASSANDRA_HOST $CASSANDRA_PORT


if [ $? -eq 0 ]
then
  echo "Cassandra setup successfully."
else
  echo "Cassandra setup failed."
  exit 1
fi