import oci

from oci.signer import Signer
from typing import Tuple
from auth.auth_provider import AuthProvider
from loguru import logger



class UserPrincipalProvider(AuthProvider):
    """
    User Principal provider class for OCI authZ/N config and signer creation.
    """

    def __init__(self, oci_config_path: str = None, config_profile: str = None):
        self.config = oci_config_path
        self.config_profile = config_profile

    def create_signer(self) -> Tuple[dict, Signer]:
        try:
            oci_config = oci.config.from_file(
                file_location=(self.config or oci.config.DEFAULT_LOCATION),
                profile_name=(self.config_profile or oci.config.DEFAULT_PROFILE),
            )
            signer = oci.signer.Signer(tenancy=oci_config["tenancy"], user=oci_config["user"], fingerprint=oci_config["fingerprint"],
                private_key_file_location=oci_config.get("key_file"),
                pass_phrase=oci.config.get_config_value_or_default(
                    oci_config, "pass_phrase"
                ),
                private_key_content=oci_config.get("key_content"),
            )
            return oci_config, signer

        except Exception:
            logger.error("Error obtaining user principal token, aborting.")
            raise SystemExit
