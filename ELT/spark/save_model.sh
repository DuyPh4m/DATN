MODEL_NAME=$1
USER_ID=$2

docker exec -it spark-master /bin/sh -c \
"pip install numpy && spark-submit --master spark://spark-master:7077 --deploy-mode client --conf saprk.dynamicAllocation.enabled=true /app/save_model.py $MODEL_NAME $USER_ID"

if [ $? -eq 0 ]
then
  echo "Spark job submitted successfully."
else
  echo "Spark job submission failed."
  exit 1
fi