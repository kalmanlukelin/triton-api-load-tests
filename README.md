# Load Test for Triton API

run.sh contains main execution logic to start load testing for Triton API. To change running time, change `export RUNNING_TIME=3000` to the number needed which is in seconds.
```
# To start the load testing
$ ./run.sh


# Tbe following is URL to view the performance metrics from locust web UI
$ http://localhost:8089/
```