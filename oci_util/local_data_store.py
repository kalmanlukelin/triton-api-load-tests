import os
import shutil
import logging
from pathlib import Path

from ..data_store import DataStore
from ..object_uri import ObjectUri
from ..logging_util.logging import CustomizeLogger

logger = CustomizeLogger.make_logger()


class LocalDataStore(DataStore):
    """
    Data store that uses data from local file system.
    """

    def __init__(self, working_dir: str):
        self.working_dir = working_dir

    def download(self, source: ObjectUri, target: str) -> bool:
        logger.debug(
            f'Got download request: {source}, checking against local file system.')
        src = os.path.join(self.working_dir, source.object_name)
        Path(os.path.dirname(target)).mkdir(parents=True, exist_ok=True)
        return shutil.copyfile(src, target)

    def upload(self, source: str, target: ObjectUri) -> bool:
        logger.debug(
            f'Got upload request: {source}, always returning True.')
        target = os.path.join(self.working_dir, target.object_name)
        Path(os.path.dirname(target)).mkdir(parents=True, exist_ok=True)
        return shutil.copyfile(source, target)