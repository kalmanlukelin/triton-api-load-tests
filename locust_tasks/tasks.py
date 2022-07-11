from locust import HttpUser
from locust_tasks.vs_model_tasks import MultiDataImageModelTaskJson
import os

SERVICE_NAME=os.environ.get("SERVICE_NAME")
SERVICE_NAMESPACE=os.environ.get("SERVICE_NAMESPACE")
HOST = f"http://{SERVICE_NAME}.{SERVICE_NAMESPACE}:8000" if SERVICE_NAME and SERVICE_NAMESPACE else "http://localhost:8000"

class ImageModel(HttpUser):
    host = HOST
    tasks = [MultiDataImageModelTaskJson]
