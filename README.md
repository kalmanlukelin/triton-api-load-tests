# Load Test for Triton API

The following are the steps to launch load testing for Triton api. `run.sh` contains main execution logic to start load testing for Triton API. To change running time, change `export RUNNING_TIME=3000` to the number needed which is in seconds.
```
# Set virtual environment for load testing
$ python3 -m venv venv

# Install related packages
$ pip3 install -r requirements.txt

# Launch virtual environment
$ source venv/bin/activate

# Start the load testing
$ ./run.sh

# To view the performance metrics from locust web UI, enter the following URL in the browser
$ http://localhost:8089/
```