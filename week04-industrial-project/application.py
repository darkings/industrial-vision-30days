import json
from logging import LoggerAdapter

from camera.factory import create_image_source
from core.catalog import load_keycap_catalog
from core.config_models import RuntimeConfig
from core.context import RunContext
from core.exceptions import NoImageAvailableError
from core.exit_codes import ExitCode


class InspectionApplication:
    """检测应用主类"""

    def __init__(
        self, config: RuntimeConfig, context: RunContext, logger: LoggerAdapter
    ):
        """初始化检测应用实例"""

        self.config = config
        self.context = context
        self.logger = logger

    def run(self) -> ExitCode:
        """完整的检测流程"""

        catalog = load_keycap_catalog(self.config.main_config.input.catalog_path)
        source = create_image_source(self.config, catalog)
        with source:
            image_input = source.read()
            if image_input is None:
                raise NoImageAvailableError(source=source.__class__.__name__)
            self.logger.info(f"image_shape:{image_input.image.shape}")
            self.logger.info(f"image_id:{image_input.image_id}")
            self.logger.info(f"product_id:{image_input.product_id}")
            self.logger.info(f"batch_id:{image_input.batch_id}")
            self.logger.info(f"captured_at:{image_input.captured_at}")
            self.logger.info(f"source_type:{image_input.source_type}")
            self.logger.info(f"source_path:{image_input.source_path}")
            self.logger.info(
                f"metadata:{json.dumps(image_input.metadata, ensure_ascii=False)}"
            )
        return ExitCode.SUCCESS
