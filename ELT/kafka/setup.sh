sudo docker exec -it kafka /bin/sh -c \
"/opt/bitnami/kafka/bin/kafka-topics.sh --create --if-not-exists --topic labeled --replication-factor 1 --partitions 1 --bootstrap-server kafka:9092"
# "cd /opt/bitnami/kafka/bin && kafka-topics.sh --bootstrap-server  zookeeper:2181 --delete --topic EPL"
sudo docker exec -it kafka /bin/sh -c \
"/opt/bitnami/kafka/bin/kafka-topics.sh --create --if-not-exists --topic raw --replication-factor 1 --partitions 1 --bootstrap-server kafka:9092"

# sudo docker exec -it kafka /bin/sh -c \
# "cd /opt/bitnami/kafka/bin && kafka-topics.sh --create zookeeper:2181 --replication-factor 1 --partitions 1 --topic EPL"
# sudo docker exec -it kafka /bin/sh -c \
# "cd /opt/bitnami/kafka/bin && kafka-topics.sh --list zookeeper:2181"

if [ $? -eq 0 ]
then
  echo "Kafka setup successfully."
else
  echo "Kafka setup failed."
  exit 1
fi
