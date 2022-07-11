#!/bin/bash

# For local testing, specify the model name with the following env variable like ic.
# export SERVICE_NAME="load-test-pre-trained-ic-vs-model"
# export MODEL_NAME="ic"
# export SERVICE_NAMESPACE="test"
# export NUMBER_OF_USERS=1
# export SPAWN_RATE=1
# export RUNNING_TIME=10
# export IMAGE_VERSION="1.0.0"
# export PRINCIPAL="user_principal"

CMD="python3 -m run"
echo "Executing $CMD"
$CMD
sleep 30
