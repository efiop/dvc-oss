import logging
import os
import threading

from dvc.utils.objects import cached_property
from dvc_objects.fs.base import ObjectFileSystem
from funcy import wrap_prop

logger = logging.getLogger(__name__)


# pylint:disable=abstract-method
class OSSFileSystem(ObjectFileSystem):
    protocol = "oss"
    REQUIRES = {"ossfs": "ossfs"}
    PARAM_CHECKSUM = "etag"
    LIST_OBJECT_PAGE_SIZE = 100

    def _prepare_credentials(self, **config):
        login_info = {}
        login_info["key"] = config.get("oss_key_id") or os.getenv(
            "OSS_ACCESS_KEY_ID"
        )
        login_info["secret"] = config.get("oss_key_secret") or os.getenv(
            "OSS_ACCESS_KEY_SECRET"
        )
        login_info["endpoint"] = config.get("oss_endpoint")
        return login_info

    @wrap_prop(threading.Lock())
    @cached_property
    def fs(self):
        from ossfs import AioOSSFileSystem as _OSSFileSystem

        return _OSSFileSystem(**self.fs_args)

    @classmethod
    def _strip_protocol(cls, path: str) -> str:
        from fsspec.utils import infer_storage_options

        options = infer_storage_options(path)
        return options["host"] + options["path"]

    def unstrip_protocol(self, path):
        return "oss://" + path.lstrip("/")
