from abc import ABC, abstractmethod
from object_uri import ObjectUri


class DataStore(ABC):
    """
    Base class for data store that handles uploading and downloading files.
    """

    @abstractmethod
    def download(self, source: ObjectUri, target: str) -> bool:
        pass

    @abstractmethod
    def upload(self, source: str, target: ObjectUri) -> bool:
        pass

    @abstractmethod
    def get_namespace(self, compartment_id: str):
        pass
