import os

from data_store import DataStore
from object_uri import ObjectUri
from oci_util.casper_client import CasperClient
from auth.auth_provider import AuthProvider
from loguru import logger
from pathlib import Path



class CasperDataStore(DataStore):
    """
    Data store that uses data from local file system.
    """

    def __init__(self, auth_provider: AuthProvider):
        self.casper_client = CasperClient(auth_provider)

    def download(self, source: ObjectUri, target: str) -> bool:
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        logger.debug(
            f'Got download request: {source}, checking against OCI object storage service.')
        obj = self.casper_client.find_object(namespace=source.namespace, bucket_name=source.bucket_name,
                                             object_name=source.object_name)
        with open(target, 'wb') as f:
            for chunk in obj.data.raw.stream(1024 * 1024, decode_content=False):
                f.write(chunk)
        logger.debug(
            f'downloaded {source.object_name} in {target} from bucket {source.bucket_name} and namespace {source.namespace}')
        return os.path.exists(target)

    def upload(self, source: str, target: ObjectUri) -> bool:
        logger.debug(
            f'Got upload request: {source}.')
        self.casper_client.upload_to_object_storage(namespace=target.namespace,
                                                    bucket=target.bucket_name,
                                                    path=source,
                                                    object_name=target.object_name)
        return True

    def get_namespace(self):
        """
        Return the namespace name of the object storage.
        :return: namespace name
        """
        return self.casper_client.get_namespace()
