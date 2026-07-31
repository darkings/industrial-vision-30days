from logging import LoggerAdapter

from core import FeatureNotImplementedError, KeycapCatalog, RuntimeConfig

from .hik_camera import HikCameraSource
from .image_source import ImageSource
from .local_source import LocalImageSource


def create_image_source(
    config: RuntimeConfig, catalog: KeycapCatalog, logger: LoggerAdapter
) -> ImageSource:
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
        return HikCameraSource(
            camera_config=config.main_config.camera,
            batch_id=config.main_config.input.batch_id,
            product=catalog.get_product(product_id=config.main_config.input.product_id),
            logger=logger,
        )
