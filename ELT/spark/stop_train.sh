TRAIN_PROCESS=$1

docker exec -it spark-master /bin/sh -c \
"PID=\$(ps -ef | grep $TRAIN_PROCESS | grep -v grep | awk '{print \$2}'); \
if [ -z \"\$PID\" ]; then echo 'No process found.'; else kill \$PID; fi"

if [ $? -eq 0 ]
then
  echo "Spark job stop successfully."
else
  echo "Spark job stop failed."
  exit 1
fi