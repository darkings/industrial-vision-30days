from logging import LoggerAdapter

from core import InputSourceError, KeycapCatalog, RuntimeConfig

from camera import DirectoryImageSource

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
        return DirectoryImageSource(
            directory=config.main_config.input.directory_path,
            allowed_extensions=config.main_config.input.allowed_extensions,
            catalog=catalog,
            batch_id=config.main_config.input.batch_id,
        )
    if config.main_config.input.source == "camera":
        return HikCameraSource(
            camera_config=config.main_config.camera,
            batch_id=config.main_config.input.batch_id,
            product=catalog.get_product(product_id=config.main_config.input.product_id),
            logger=logger,
        )
    raise InputSourceError(config.main_config.input.source)
