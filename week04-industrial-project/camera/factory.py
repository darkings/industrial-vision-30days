from core.catalog import KeycapCatalog
from core.config_models import RuntimeConfig
from core.exceptions import FeatureNotImplementedError

from camera.image_source import ImageSource
from camera.local_source import LocalImageSource


def create_image_source(config: RuntimeConfig, catalog: KeycapCatalog) -> ImageSource:
    if config.main_config.input.source == "image":
        return LocalImageSource(
            image_path=config.main_config.input.image_path,
            batch_id=config.main_config.input.batch_id,
            allowed_extensions=config.main_config.input.allowed_extensions,
            product=catalog.get_product(product_id=config.main_config.input.product_id),
        )

    if config.main_config.input.source == "directory":
        raise FeatureNotImplementedError("directory功能尚未实现")
    if config.main_config.input.source == "camera":
        raise FeatureNotImplementedError("camera功能尚未实现")
