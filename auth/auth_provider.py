from typing import Tuple
from abc import abstractmethod, ABC
from oci.signer import Signer


class AuthProvider(ABC):
    """
    Base class for OCI authZ/N config and singer creation.
    """

    @abstractmethod
    def create_signer(self) -> Tuple[dict, Signer]:
        pass