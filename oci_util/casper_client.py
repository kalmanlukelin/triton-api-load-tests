import oci
import os

from auth.auth_provider import AuthProvider
from loguru import logger



class CasperClient(object):
    def __init__(self, auth_provider: AuthProvider):
        """
        Casper Client that has appropriate signer and public methods to use.
        """

        self.auth_provider = auth_provider
        self.casper_client = self._create_object_storage_client()

    def _create_object_storage_client(self) -> object:
        oci_config, signer = self.auth_provider.create_signer()
        client = oci.object_storage.ObjectStorageClient(config=oci_config, signer=signer)
        return client

    # PUBLIC API ======================================================================

    def get_namespace(self):
        """
        Return the namespace name of the object storage.
        :return: namespace name
        """
        return self.casper_client.get_namespace().data

    def find_object(self,
                    namespace: str,
                    bucket_name: str,
                    object_name: str) -> object:
        """
        Find the object given object name and bucket name, store it in the object list and return
        :param namespace: object storage namespace
        :param bucket_name: bucket name
        :param object_name: object name
        :return: object from oci object storage
        """
        client = self.casper_client
        try:
            obj = client.get_object(namespace, bucket_name, object_name)
            return obj

        except oci.exceptions.ServiceError as e:
            ret = (e.status == 404)
            """
            404 means the object was absent in the bucket but the pull succeeded ie.
            we were able to contact casper and locate the bucket. do not treat
            empty bucket as an err. report the status of the pull alone and return
            an empty object_list.
            """
            if ret:
                logger.info(f"Object NOT found for bucket<{bucket_name}>, namespace<{namespace}>, object<{object_name}>: {e}")
            else:
                logger.error(f"GET failed for bucket<{bucket_name}>, namespace<{namespace}>, object<{object_name}>: {e}")

        except Exception as e:
            logger.error(f"GET failed for bucket<{bucket_name}>, namespace<{namespace}>, object<{object_name}>: {e}")

    def upload_to_object_storage(self, namespace: str, bucket: str, object_name: str, path: str):
        """
        upload_to_object_storage will upload a single file to an object storage bucket.
        :param bucket: Name of the bucket in which the object will be stored
        :param namespace: Name of the namespace object
        :param object_name: object name
        :param path: path to file to upload to object storage
        :rtype: None
        """
        with open(path, "rb") as in_file:
            name = object_name or os.path.basename(path)
            self.casper_client.put_object(namespace_name=namespace,
                                          bucket_name=bucket,
                                          object_name=object_name,
                                          put_object_body=in_file)
            logger.info("Finished uploading {}".format(name))
