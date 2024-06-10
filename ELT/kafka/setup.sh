docker exec -it kafka /bin/sh -c \
"/opt/bitnami/kafka/bin/kafka-topics.sh --create --if-not-exists --topic labeled --replication-factor 1 --partitions 1 --bootstrap-server kafka:9092"

docker exec -it kafka /bin/sh -c \
"/opt/bitnami/kafka/bin/kafka-topics.sh --create --if-not-exists --topic classify --replication-factor 1 --partitions 1 --bootstrap-server kafka:9092"

if [ $? -eq 0 ]
then
  echo "Kafka setup successfully."
else
  echo "Kafka setup failed."
  exit 1
fi
