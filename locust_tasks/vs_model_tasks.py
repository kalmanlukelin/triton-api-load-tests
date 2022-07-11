from locust import task, TaskSet
import os
from os.path import isfile, join
from os import listdir
from locust_tasks.commons.local_data_store import get_encoded_image
from loguru import logger
import json, base64

# Get current path
CUR_PATH = os.path.dirname(os.path.realpath(__file__))

# Pre-define all path for different resolution images and pdfs
IMG_RESOURCES = {
    "low-res-img": f"{CUR_PATH}/resources/load-test-low-res-image_computer.jpg",
    "mid-res-img": f"{CUR_PATH}/resources/load-test-mid-res-image_street_view.jpg",
    "high-res-img": f"{CUR_PATH}/resources/load-test-high-res-image_lavatory.jpg",
    "ultra-res-img": f"{CUR_PATH}/resources/load-test-ultrahigh-res-image_office.jpg",
    "low-res-doc": f"{CUR_PATH}/resources/load-test-detect-text-image_receipt.jpg",
    "low-res-pdf": f"{CUR_PATH}/resources/load-test-detect-text-image_one_page.pdf",
    "high-res-pdf": f"{CUR_PATH}/resources/load-test-detect-text-image_essay.pdf",
    "ultra-res-doc": f"{CUR_PATH}/resources/load-test-detect-text-image_big_small.jpg",
    "random-images": f"{CUR_PATH}/resources/images",
    "random-documents": f"{CUR_PATH}/resources/documents",
}

TESTING_IMG = {
    "ocr": f"{CUR_PATH}/resources/load-test-detect-text-image_receipt.jpg",
    "dc": f"{CUR_PATH}/resources/book-page.jpg",
    "ld": f"{CUR_PATH}/resources/book-page.jpg",
    "ic": f"{CUR_PATH}/resources/furniture.json",
    "od": f"{CUR_PATH}/resources/furniture.json",
}

TESTING_URL = {
    "ic": "/v2/models/ic_full/infer",
    "od": "/v2/models/OD_full/infer",
}


class MultiDataImageModelTaskJson(TaskSet):
    """Load test models running in OKE. Only support IC/OD and OCR models."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.body = None

    def on_start(self):
        """
        Initializing signer and request body for http clients.
        """
        self.model_name = os.environ.get("MODEL_NAME")
        self.testing_url = TESTING_URL.get(self.model_name)
        self.body = self._define_request_body()
        logger.info(self.client.base_url)
        self.len_body = len(self.body)
        self.idx = 0

    @task(1)
    def predict(self):
        """
        Sending request to prediction endpoint, and log prediction latency.
        """
        rsp = self.client.post(self.testing_url, json=self.body[self.idx % self.len_body])
        self.idx += 1

    def _define_request_body(self):
        """
        Define request body for model prediction, only supports IC/OD and OCR models.
        """
        request_bodies = []

        image_path = f"{CUR_PATH}/resources/images"
        images = [f for f in listdir(
            image_path) if isfile(join(image_path, f))]
        for image_name in images:
            # convert image into json file
            with open(f"{CUR_PATH}/resources/images/{image_name}", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                image = encoded_string.decode('utf-8')
                with open(f"{image_name.split('.')[0]}.json", "w") as fp:
                    query = { "maxResults": 5, "image": { "data": image } }
                    request = {
                        "inputs": [ {"name": "REQUEST", "shape": [ 1 ], "datatype": "BYTES", "data": [ json.dumps(query) ] } ],
                        "outputs": [ {"name": "RESPONSE"} ]
                    }
                    json.dump(request, fp)
            with open(f"{image_name.split('.')[0]}.json", "rb") as image_file:
                request_bodies.append(json.load(image_file))
        return request_bodies

class ImageModelTasks(TaskSet):
    """Load test models running in OKE. Only support IC/OD and OCR models."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.body = None

    def on_start(self):
        """
        Initializing signer and request body for http clients.
        """
        self.model_name = os.environ.get("MODEL_NAME")
        self.body = self._define_request_body()
        logger.info(self.client.base_url)
        self.testing_url = TESTING_URL.get(self.model_name)

    @task(1)
    def predict(self):
        """
        Sending request to prediction endpoint, and log prediction latency.
        """
        rsp = self.client.post(self.testing_url, json=self.body)

    def _define_request_body(self):
        """
        Define request body for model prediction, only supports IC/OD and OCR models.
        """
        image_path = None
        file_type = "image"
        features = None
        if "ic" in self.model_name:
            image_path = TESTING_IMG.get("ic", IMG_RESOURCES["low-res-img"])
            features = [
                {
                    "featureType": "IMAGE_CLASSIFICATION",
                    "maxResults": 3,
                }
            ]
        elif "dc" in self.model_name:
            image_path = TESTING_IMG.get("dc", IMG_RESOURCES["low-res-img"])
            features = [
                {
                    "featureType": "DOCUMENT_CLASSIFICATION",
                    "maxResults": 3,
                }
            ]
            file_type = "document"
        elif "od" in self.model_name:
            image_path = TESTING_IMG.get("od", IMG_RESOURCES["low-res-img"])
            features = [
                {
                    "featureType": "OBJECT_DETECTION",
                    "maxResults": 3,
                }
            ]
        elif "ld" in self.model_name:
            image_path = TESTING_IMG.get("ld", IMG_RESOURCES["low-res-img"])
            features = [
                {
                    "featureType": "LANGUAGE_CLASSIFICATION",
                    "maxResults": 3,
                }
            ]
            file_type = "document"
        elif "kv" in self.model_name:
            image_path = TESTING_IMG.get("ocr", IMG_RESOURCES["low-res-img"])
            features = [
                {"featureType": "KEY_VALUE_DETECTION"},
            ]
            file_type = "document"
        elif "ocr" in self.model_name:
            image_path = TESTING_IMG.get("ocr", IMG_RESOURCES["low-res-img"])
            features = [
                {"featureType": "TEXT_DETECTION"},
            ]
            file_type = "document"
        elif "td" in self.model_name:
            image_path = TESTING_IMG.get("ocr", IMG_RESOURCES["low-res-img"])
            features = [
                {"featureType": "TABLE_DETECTION"},
            ]
            file_type = "document"
        else:
            raise Exception(
                f"Unrecognized model name: {self.model_name}. Unable to generate requests.")

        _, image_byte = get_encoded_image(
            image_name=image_path
        )
        image_name = image_path.split("/")[-1]
        logger.info(
            f"Testing model: {self.model_name}. Testing image: {image_name}")

        with open(image_path, "rb") as image_file:
            return json.load(image_file)
