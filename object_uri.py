class ObjectUri(object):
    """
    Denotes a object location in OCI object storage.
    """

    def __init__(self, namespace: str, bucket_name: str, object_name: str):
        self.namespace = namespace
        self.bucket_name = bucket_name
        self.object_name = object_name

    @staticmethod
    def create(namespace: str, bucket_name: str, object_name: str):
        if not namespace or not bucket_name or not object_name:
            return None
        return ObjectUri(namespace, bucket_name, object_name)

    def __repr__(self) -> str:
        return '/'.join((self.namespace, self.bucket_name, self.object_name))