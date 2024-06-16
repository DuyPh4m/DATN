docker exec -it spark-master /bin/sh -c \
"PID=\$(ps -ef | grep 'classify.py' | grep -v grep | awk '{print \$2}'); \
if [ -z \"\$PID\" ]; then echo 'No labeling.py process found.'; else kill \$PID; fi"

if [ $? -eq 0 ]
then
  echo "Spark job stop successfully."
else
  echo "Spark job stop failed."
  exit 1
fi