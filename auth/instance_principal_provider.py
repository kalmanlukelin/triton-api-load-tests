import oci

from oci.signer import Signer
from typing import Tuple
from auth.auth_provider import AuthProvider
from loguru import logger



class InstancePrincipalProvider(AuthProvider):
    """
    Instance Principal provider class for OCI authZ/N config and signer creation.
    """

    def create_signer(self) -> Tuple[dict, Signer]:
        try:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            oci_config = {'region': signer.region, 'tenancy': signer.tenancy_id}
            return oci_config, signer

        except Exception:
            logger.error("Error obtaining instance principal token, aborting.")
            raise SystemExit
