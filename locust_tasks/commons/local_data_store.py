import base64
from typing import Tuple


def get_encoded_image(image_name: str) -> Tuple[str, bytes]:
    """
    Get sample image from local disk and return its byte and image name
    :param image_name:
    :return: Tuple[image name, image file byte]
    """
    with open(image_name, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return image_name, encoded_string
