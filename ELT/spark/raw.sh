docker exec -it spark-master /bin/sh -c \
"spark-submit --master spark://spark-master:7077 --deploy-mode client --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,com.datastax.spark:spark-cassandra-connector_2.12:3.1.0 --conf saprk.dynamicAllocation.enabled=true  /app/raw.py"

if [ $? -eq 0 ]
then
  echo "Spark job submitted successfully."
else
  echo "Spark job submission failed."
  exit 1
fi